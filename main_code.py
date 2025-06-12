import speech_recognition as sr
import pyttsx3
import time
from datetime import datetime
import re

# --- Configuración del motor de voz ---
engine = pyttsx3.init()

def AssistantResponse(text):
    """
    Hace que el asistente hable el texto proporcionado.
    """
    engine.say(text)
    engine.runAndWait()

def SpeechToText(device_index=2, max_retries=3, retry_delay=2):
    """
    Escucha a trávez del microfono, reconoce el habla y lo convierte a texto
    Si no se escucha nada o hay error, devuelve cadena vacia
    """
    r=sr.Recognizer()

    # r.pause_threshold: Segundos de silencio después de los cuales una frase se considera completa.
    # Un valor más bajo (ej. 0.5 - 0.7) puede hacer que el asistente corte antes,
    # lo cual es útil si hablas rápido y sin muchas pausas.
    r.pause_threshold=0.7 # Valor recomendado

    # r.dynamic_energy_threshold: Si es True, el umbral de energía se ajusta automáticamente
    # basado en el nivel de ruido ambiental.
    r.dynamic_energy_threshold=True # Se recomienda dejarlo por defecto

    with sr.Microphone(device_index=device_index) as source:
        print("Ajustando para ruido ambiental ... ")
        r.adjust_for_ambient_noise(source, duration=1) # Aumentar si el ambiente es muy ruidoso
        #print(f"Umbral ajustado a: {r.energy_threshold}")
        
        print("Escuchando ... ")
        try:
            # r.listen(source, timeout, phrase_time_limit)
            # timeout: Máximo de segundos que esperará antes de asumir que el silencio significa el final de la frase.
            #          Si el usuario no empieza a hablar en este tiempo, lanzará WaitTimeoutError.
            # phrase_time_limit: Máximo de segundos que grabará una frase antes de cortarla.
            #                    Útil si el usuario habla muy largo y no quieres esperar.
            audio=r.listen(source, timeout=5, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            print("No se detecta la voz (timeout).")
            return "" # Si no hay audio, retorna vacio
        except Exception as ex:
            print(f"Error al escuchar el micrófono: {ex}")
            return ""
    print("Reconociendo ... ")
    for attempt in range(max_retries):
        try:
            texto=r.recognize_google(audio,language='es-ES')
            #print(f"El usuario dijo: {texto}")
            return texto
        except sr.UnknownValueError:
            print("No pude entender lo que dijiste.")
            return ""
        except sr.RequestError as ex:
            print(f"Error en el servicio de reconocimiento de Google (intento {attempt+1}/{max_retries}): {ex}")
            if attempt < max_retries-1:
                print(f"Reintentando en {retry_delay} segundos ... ")
                time.sleep(retry_delay)
            else:
                print("Se agotaron los intetos para el reconocimiento de voz.")
                return ""
        except Exception as ex:
            print(f"Ocurrio un error inesperado al reconocer: {ex}")
            return ""
    return "" # En caso de que todos los reintentos fallen

# --- Funciones de Manejo de Comandos (Handlers) ---

def time_command():
    """Maneja el comando para decir la hora actual."""
    hora = datetime.now().strftime("%H:%M")
    AssistantResponse(f'La hora es {hora}')

def how_are_you_command():
    """Maneja el comando para preguntar cómo está el asistente."""
    AssistantResponse('Estoy aprendiendo contigo.')

def sum_command(user_text):
    """Maneja el comando de suma, extrayendo números de la frase."""
    numbers=re.findall()

def exit_command():
    """Maneja los comandos para salir del asistente."""
    AssistantResponse("Hasta luego, ¡que tengas un buen día!")
    # Nota: El 'break' para salir del bucle principal se maneja en AssistantExecute
    return "exit" # Indicador para la función principal de que debe salir

def unknown_command():
    """Maneja comandos no reconocidos."""
    AssistantResponse('No entendí eso. ¿Podrías repetirlo o intentar otra cosa?')


# --- Mapeo de Comandos ---
# Este diccionario mapea una palabra clave o una tupla de palabras clave
# a la función que debe manejar el comando.
# Las funciones de manejo deben aceptar el texto completo del usuario si necesitan procesarlo (como en suma).
# El orden aquí importa si hay solapamiento, las más específicas primero.
COMMANDS = {
    ("hora"): time_command,
    ("cómo estás", "como estas"): how_are_you_command,
    ("suma", "cuánto es", "cuanto es"): sum_command, # Esta manejará el texto completo
    ("adiós", "adios", "salir", "cierra"): exit_command,
}

def AssistantExecute():
    """
    Función principal que ejecuta el asistente, usando una estructura modular para los comandos.
    """
    AssistantResponse("Hola, ¿en qué puedo ayudarte hoy?")

    while True:
        UserText = SpeechToText()

        if UserText:
            UserText_lower = UserText.lower()
            command_executed = False

            # Itera sobre los comandos en el diccionario
            for keywords, functions in COMMANDS.items():
                # Convierte las keywords a una tupla si no lo son (para manejo de un solo keyword)
                if not isinstance(keywords, tuple):
                    keywords = (keywords,)

                # Comprueba si alguna de las palabras clave está en el texto del usuario
                for keyword in keywords:
                    if keyword in UserText_lower:
                        # Si la función necesita el texto completo (como 'suma'), pásaselo.
                        # Esto es una forma simple; para más complejidad, usarías un sistema de "intenciones".
                        if functions == sum_command:
                            result = functions(UserText_lower)
                        else:
                            result = functions() # Para funciones que no necesitan el texto completo
                        
                        command_executed = True
                        if result == "exit": # Si el handler_function indicó que es un comando de salida
                            return # Sale de la función AssistantExecute y termina el programa
                        break # Rompe el bucle interno de keywords, ya encontramos un match
                if command_executed:
                    break # Rompe el bucle externo de COMMANDS, ya ejecutamos un comando
            
            if not command_executed:
                unknown_command() # Si ningún comando fue reconocido
        else:
            print("Esperando una nueva instrucción ... ")
            AssistantResponse('No te escuché, ¿hay algo en lo que pueda ayudarte?')

# --- Ejecución del asistente ---
if __name__ == "__main__":
    AssistantExecute()
