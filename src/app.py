"""
app.py — Frontend ligero con Streamlit para conversar con un Assistant de OpenAI.

Responsabilidades:
- Cargar variables de entorno (OPENAI_API_KEY, ASSISTANT_ID, etc.).
- Renderizar UI (logo, título, historial, input del chat).
- Mantener estado de conversación en Streamlit (thread_id, historial).
- Enviar mensajes del usuario al thread del Assistant.
- Crear y monitorear un "run" del Assistant (ejecución) vía utils.run_excecuter.
- Mostrar la última respuesta del Assistant con efecto "typewriter".

Requisitos:
- Variables en entorno: OPENAI_API_KEY, ASSISTANT_ID.
- utils.py debe exponer run_excecuter(run) y tener un cliente OpenAI compatible.
- Imagen del logo en ruta 'src/images/datapath-logo.png' (ruta relativa al CWD).
"""

import streamlit as st
from PIL import Image  # Manejo de imágenes
import time
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (en local). En producción, usa st.secrets o variables del contenedor.
load_dotenv()

import os
from utils import run_excecuter
from openai import OpenAI


# 1) Inicializar cliente de OpenAI con la API Key del entorno
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 2) Assistant ID (el asistente ya configurado en OpenAI)
assistant_id = os.getenv("ASSISTANT_ID")
print("assistant id: ", assistant_id)  # Útil para trazas en logs

# 3) Encabezado y branding de la app
#image = Image.open('src/images/datapath-logo.png')  # Asegúrate de que exista en esa ruta en el contenedor
#st.image(image, use_container_width=True)

# 4) Título principal
st.title("Asistente de Open AI [ Carlos Sánchez 🦕 ]")

# 5) Estado de sesión (persistente entre interacciones en la misma sesión del usuario)
#    - thread_id: ID del "hilo" de conversación en OpenAI (persistente)
#    - messages: historial básico mostrado en la UI (para re-render de Streamlit)
if "thread_id" not in st.session_state:
    st.session_state.thread_id = client.beta.threads.create().id  # Crear un thread vacío una sola vez
if "messages" not in st.session_state:
    st.session_state.messages = []

# 6) Re-pintar mensajes previos del historial en la UI
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7) Efecto "máquina de escribir" para la respuesta del assistant (puro azúcar visual)
def typewriter(text: str, speed: int):
    """
    Muestra 'text' progresivamente a 'speed' tokens por segundo, simulando tecleo.
    - text: texto completo a renderizar
    - speed: tokens/seg (a mayor número, más rápido)
    """
    tokens = text.split()
    container = st.empty()
    for index in range(len(tokens) + 1):
        curr_full_text = " ".join(tokens[:index])
        container.markdown(curr_full_text)
        time.sleep(1 / speed)

# 8) Entrada del usuario (componente de chat nativo de Streamlit)
if prompt := st.chat_input("Escribir mensaje..."):
    # 8.1) Guardar y renderizar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 8.2) Enviar el mensaje al thread del Assistant en OpenAI
    with st.chat_message("assistant"):
        # Crear mensaje en el thread (rol user)
        _ = client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )

        # 8.3) Lanzar un "run" (ejecución) para que el Assistant procese el thread actual
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id
        )

        # 8.4) Mostrar spinner mientras se procesa (y ejecutar tools si el Assistant lo requiere)
        with st.spinner('El asistente de OpenAI está escribiendo ... ⏳'):
            st.toast('Conexión con Google Cloud Platform y OpenAI API éxitosas ✅', icon='🎉')

            # Bloquea hasta que el run termine o hasta que se resuelvan tool-calls.
            run_excecuter(run)

            # 8.5) Recuperar la última respuesta del Assistant en el thread
            # Nota: .list() devuelve mensajes con .data en orden desc (más reciente primero).
            # Tomamos el primer mensaje y su primer fragmento de texto.
            last_msg = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            ).data[0]

            # En algunos casos un mensaje puede tener múltiples "content parts";
            # aquí asumimos uno de tipo texto:
            message_assistant = last_msg.content[0].text.value

        # 8.6) Renderizar con "typewriter"
        typewriter(message_assistant, 50)

    # 8.7) Persistir respuesta en el historial de la UI
    st.session_state.messages.append({"role": "assistant", "content": message_assistant})
