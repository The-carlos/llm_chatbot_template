#gmail
from email.message import EmailMessage
import smtplib

##google sheets
import pandas as pd
import pygsheets

##whatsapp 
from heyoo import WhatsApp

#openai
from openai import OpenAI
from time import sleep
import json

##Obtener el api key
from dotenv import load_dotenv
import os
load_dotenv()

##credenciales
APP_PASSWORD_GMAIL=os.getenv("APP_PASSWORD_GMAIL")
CORREO_REMITENTE=os.getenv("EMAIL_REMITENTE")
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
WHATSAPP_API_TOKEN=os.getenv("WHATSAPP_API_TOKEN")
PHONE_NUMBER_ID=os.getenv("PHONE_NUMBER_ID")
GOOGLE_SHEETS_ID= os.getenv("GOOGLE_SHEETS_ID")


client = OpenAI(api_key=OPENAI_API_KEY) 


#----------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------
#------------------------------------------------ conexion a email ----------------------------------------------------
def enviar_correo(nombre_lead,correo_lead,mensaje_para_lead):
  try:
    remitente = CORREO_REMITENTE #host
    destinatario = correo_lead
    mensaje = mensaje_para_lead

    email = EmailMessage()
    email["From"] = remitente
    email["To"] = destinatario
    email["Subject"] = "Un LMM tiene un correo para ti 🤖" + nombre_lead
    email.set_content(mensaje)
    smtp = smtplib.SMTP_SSL("smtp.gmail.com")
    print(APP_PASSWORD_GMAIL)
    smtp.login(remitente, APP_PASSWORD_GMAIL)
    smtp.sendmail(remitente, destinatario, email.as_string())
    smtp.quit()
    return True
  except Exception as e:
    print(e)
    return False

#----------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------
#-------------------------------------------- conexion a google sheets ------------------------------------------------
def registrar_google_sheets(nombre,correo,programa):
  ##obtener los datos de google sheets
  sheet_id=GOOGLE_SHEETS_ID
  sheet_name="Interesados"
  url=f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

  ##añadimos el nuevo registro al dataframe
  df=pd.read_csv(url)
  print(df)

  df.loc[len(df.index)] = ['123',nombre,correo,programa]
  print(df)

  try:
    ##luego cargamos a google sheets
    service_account_path='src/project-ai-engineering-be7c61d2a574.json'
    gc = pygsheets.authorize(service_file=service_account_path)

    #open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
    sh = gc.open_by_url(url)

    #select the first sheet
    wks = sh[0]
    #update the first sheet with df, starting at cell B2.
    wks.set_dataframe(df,(1,1))
    return True
  except Exception as e:
    print(e)
    return False

#----------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------
#------------------------------------------- enviar mensaje por whatsapp ----------------------------------------------
def enviar_whatsapp(numero_whatsapp_asesor,mensaje_asesor):
  #conexion a whatsapp
  """para enviar mensajea a whatsaap"""
  try:
    messenger = WhatsApp(WHATSAPP_API_TOKEN, ## TOKEN
                        phone_number_id=PHONE_NUMBER_ID #ID_NUMBER
                        )
    # For sending a Text messages
    messenger.send_message(mensaje_asesor, numero_whatsapp_asesor)
    return True
  except:
    return False

#----------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------
## Ejecutar el RUN
def run_excecuter(run):
    """
    Ejecuta de forma iterativa los tool calls (acciones) que un asistente de OpenAI solicita
    durante la ejecución de un "run" (una conversación activa en un thread).

    Este bucle consulta repetidamente el estado del "run" hasta que se completa o requiere
    una acción manual (por ejemplo, la ejecución de una función definida como tool en el backend).

    Flujo general:
    ---------------
    1. Recupera el estado actual del run usando `client.beta.threads.runs.retrieve()`.
    2. Si el estado es:
        - "completed": el asistente ya terminó su respuesta → se detiene el bucle.
        - "requires_action": el asistente solicita ejecutar una o más tools → se procesan.
        - Cualquier otro (p.ej. "in_progress"): se espera y reintenta cada 3 segundos.
    3. Si se requieren acciones (`requires_action`):
        - Se recorren las acciones solicitadas (`tool_calls`).
        - Se identifican las funciones por nombre (`accion.function.name`).
        - Se ejecutan las funciones locales correspondientes (`registrar_google_sheets`, `enviar_correo`, `enviar_whatsapp`).
        - Se recopilan los resultados en `tools_output_list`.
    4. Se reportan las salidas al asistente mediante `client.beta.threads.runs.submit_tool_outputs()`.

    Este mecanismo permite que el asistente delegue tareas reales al entorno Python,
    y que las respuestas del modelo se sincronicen con los resultados de ejecución
    (p. ej., confirmar que un correo fue enviado o que un registro se guardó en Google Sheets).

    Parámetros
    ----------
    run : openai.types.beta.threads.Run
        Objeto de tipo Run generado al iniciar una interacción con el asistente.
        Contiene los identificadores `thread_id` y `id` necesarios para hacer polling.

    Retorno
    -------
    None
        La función no retorna un valor explícito. Su propósito es ejecutar herramientas
        y actualizar el estado del run en OpenAI.

    Ejemplo
    -------
    >>> from utils import run_excecuter
    >>> run = client.beta.threads.runs.create(
    ...     thread_id=thread.id,
    ...     assistant_id="asst_123",
    ...     instructions="Registra al lead y envíale un correo."
    ... )
    >>> run_excecuter(run)
    Esperando respuesta del Asistente
    Requiere accion
    -----
    [{'id': 'toolcall_001', 'function': {...}}]
    -----
    ejecucion de acciones ha terminado
    [{'tool_call_id': 'toolcall_001', 'output': 'True'}]
    """

    while True:
        # 1️⃣ Recuperar el estado actual del run desde la API
        run_status = client.beta.threads.runs.retrieve(
            thread_id=run.thread_id,
            run_id=run.id
        )

        # 2️⃣ Si el asistente ya terminó
        if run_status.status == "completed":
            print("✅ Acción terminada.")
            break

        # 3️⃣ Si el asistente requiere ejecutar una tool
        elif run_status.status == "requires_action":
            print("⚙️  Requiere acción del backend.")

            list_of_actions = run_status.required_action.submit_tool_outputs.tool_calls
            print("-----" * 20)
            print(list_of_actions)
            print("-----" * 20)

            tools_output_list = []  # Aquí guardaremos las salidas de cada tool

            # 4️⃣ Recorremos cada acción solicitada
            for accion in list_of_actions:
                function_name = accion.function.name
                argumentos = json.loads(accion.function.arguments)

                print(f"Nombre de la función a ejecutar: {function_name}")
                print(f"Argumentos: {argumentos}")

                # 5️⃣ Ejecutar la función correspondiente según su nombre
                if function_name == "registrar_google_sheets":
                    resultado = registrar_google_sheets(
                        argumentos["nombre_lead"],
                        argumentos["correo_lead"],
                        argumentos["producto_de_interes"]
                    )

                elif function_name == "enviar_correo":
                    resultado = enviar_correo(
                        argumentos["nombre_lead"],
                        argumentos["correo_lead"],
                        argumentos["mensaje_para_lead"]
                    )

                elif function_name == "enviar_whatsapp":
                    resultado = enviar_whatsapp(
                        numero_whatsapp_asesor=argumentos["numero_whatsapp_asesor"],
                        mensaje_asesor=argumentos["mensaje_asesor"]
                    )

                else:
                    resultado = "❌ Acción desconocida."

                # 6️⃣ Agregar salida a la lista de resultados
                tools_output_list.append({
                    "tool_call_id": accion.id,
                    "output": str(resultado)
                })

            print("🧩 Ejecución de acciones terminada.")
            print(tools_output_list)

            # 7️⃣ Enviar resultados al asistente para que continúe el flujo conversacional
            client.beta.threads.runs.submit_tool_outputs(
                thread_id=run.thread_id,
                run_id=run.id,
                tool_outputs=tools_output_list
            )

        # 8️⃣ Si el asistente sigue procesando (p.ej. generando texto o esperando tools)
        else:
            print("⏳ Esperando respuesta del asistente...")
            sleep(3)



#if __name__=="__main__":
#  enviar_correo(correo_lead="kevin.inofuente.colque.27@gmail.com",mensaje_para_lead="hola", nombre_lead="kevin")