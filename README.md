# 🤖 OpenAI Assistant Template – by Carlos Sánchez 🦕  

Un proyecto base completamente funcional para crear, probar y desplegar asistentes personalizados usando la **API de OpenAI**.  
Incluye una interfaz en **Streamlit**, configuración de entorno segura con `.env`, y un flujo de control de versiones profesional con protección de secretos.  

---

## 📘 Descripción General

Este proyecto sirve como plantilla base para crear un **asistente inteligente con OpenAI Assistants API**.  
El asistente está completamente configurado desde la **OpenAI Platform** y puede interactuar mediante una **interfaz web ligera desarrollada en Streamlit**.

El flujo general de trabajo incluye:

1. Configuración del asistente en la [OpenAI Platform](https://platform.openai.com/assistants).
2. Pruebas locales con el SDK de Python de OpenAI.
3. Interfaz gráfica sencilla (tipo “Playground”) construida en Streamlit.
4. Carga segura de variables de entorno desde `.env`.
5. Control de versiones limpio con `.gitignore` y protección de secretos.

---

## 🧠 Arquitectura del Proyecto

```
llm_chatbot_template/
│
├── src/
│   ├── images/
│   │   └── datapath-logo.png       # Logo mostrado en la interfaz Streamlit
│   ├── app.py                      # Aplicación principal en Streamlit
│   └── utils/
│       └── run_excecuter.py        # Funciones auxiliares (ejecución de threads/runs)
│
├── .env                            # Variables locales (API keys, IDs)
├── .env.example                    # Plantilla sin valores reales
├── .gitignore                      # Exclusión de archivos sensibles
├── requirements.txt                # Dependencias necesarias
└── README.md                       # Este archivo :)
```

---

## ⚙️ Requisitos Previos

- Python **3.10+**
- Cuenta activa en [OpenAI Platform](https://platform.openai.com/)
- Clave API de OpenAI (regenerada y segura)
- Opcional: credenciales de Google Cloud (si se integran otros servicios)

---

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/The-carlos/llm_chatbot_template.git
cd llm_chatbot_template
```

### 2. Crear entorno virtual
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# o en Windows:
# .venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Crea un archivo `.env` basado en el ejemplo:

```bash
cp .env.example .env
```

Edita el contenido con tus credenciales:

```bash
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxx
ASSISTANT_ID=asst_xxxxxxxxxxxxxxxxxx
```

⚠️ **Importante:** nunca subas el archivo `.env` a GitHub.

---

## 🧩 Ejecución Local

Ejecuta la app en modo local:

```bash
streamlit run src/app.py
```

Esto abrirá una interfaz en tu navegador (por defecto en `http://localhost:8501`) donde podrás interactuar con tu asistente directamente, con soporte para memoria de sesión y renderizado de mensajes.

---

## 💬 Ejemplo de Flujo Interno

El archivo principal (`app.py`) sigue este flujo:

```python
# 1. Cargar claves desde .env
from dotenv import load_dotenv
load_dotenv()

# 2. Crear cliente de OpenAI
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 3. Crear un thread y enviar mensaje del usuario
thread = client.beta.threads.create()
client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Hola, ¿cómo estás?"
)

# 4. Ejecutar el asistente
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=os.getenv("ASSISTANT_ID")
)
```

---

## 🧠 Lógica de la Interfaz (Streamlit)

- Renderiza el logotipo (`datapath-logo.png`).
- Muestra título y mensajes en tiempo real.
- Mantiene el historial de conversación dentro de la sesión (`st.session_state`).
- Soporta ejecución continua con respuestas asíncronas del modelo.
- Permite reiniciar el hilo o iniciar nuevas conversaciones fácilmente.

---

## 🔐 Seguridad y Buenas Prácticas

### 🧾 `.gitignore`
El archivo `.gitignore` incluye:

```
# Variables y credenciales
.env
*.json

# Entorno virtual
.venv/

# Cache de Python
__pycache__/
*.pyc
```

### 🕵️‍♂️ GitHub Push Protection
Durante el desarrollo, GitHub bloqueó pushes que contenían:
- API keys de OpenAI
- Credenciales JSON de Google Cloud

Estos archivos se eliminaron con `git-filter-repo` y el historial fue reescrito para garantizar cero exposición.

**Comando utilizado:**
```bash
git filter-repo --force --invert-paths --path src/.env --path src/project-ai-engineering-be7c61d2a574.json
```

### ✅ Acciones posteriores
- Regeneración de llaves API.
- Reconfiguración de remoto Git con:
  ```bash
  git remote add origin https://github.com/The-carlos/llm_chatbot_template.git
  git push origin main --force
  ```

---

## 🧰 Comandos Útiles

| Acción | Comando |
|--------|----------|
| Ejecutar localmente | `streamlit run src/app.py` |
| Instalar dependencias | `pip install -r requirements.txt` |
| Crear entorno virtual | `python -m venv .venv` |
| Subir cambios | `git add . && git commit -m "update" && git push origin main` |
| Eliminar archivos sensibles del historial | `git filter-repo --invert-paths --path <archivo>` |

---

## 🌐 Despliegue (opcional)

El proyecto puede desplegarse fácilmente en:
- **Google Cloud Run**
- **Railway**
- **Render**
- **DigitalOcean App Platform**

Solo recuerda configurar las variables de entorno (`OPENAI_API_KEY`, `ASSISTANT_ID`) directamente en el panel de tu proveedor.

---

## 👨‍💻 Autor

**Carlos Enrique Sánchez Martínez**  
Data Developer · Data Science Professor · AI Engineer  
[GitHub @The-carlos](https://github.com/The-carlos)  

---

## 🪴 Licencia
MIT License © 2025 Carlos Sánchez  
Libre para uso educativo y profesional.  

---

> “Build once, deploy smart, and keep your keys safe.” 💡  
