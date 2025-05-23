import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def segmenter(transcription: str, context: str, model="gpt-4") -> dict:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Eres un asistente que segmenta transcripciones de videotutoriales."
                },
                {
                    "role": "user",
                    "content": f"""
                    A partir de la siguiente transcripción de un tutorial, tienes que dividir la transcripción en partes, sin dejar ninguna palabra fuera (es como hacer cortes en el texto original). Estos cortes deben de ser por temáticas, es decir, partes en las que se puede dividir un tutorial, por ejemplo: "Cambiar nombre", "Cambiar imagen", etc.
                    Además, para este tutorial contamos con contexto de la herramienta que estamos usando, usa esta información para hacer más precisos los cortes. El contexto es el siguiente:
                    {context}

                    **NO SE PUEDE OMITIR NINGUNA PALABRA.**  
                    Cada palabra de la transcripción DEBE aparecer UNA SOLA VEZ en alguno de los bloques.  
                    No puedes cambiar el orden de las palabras.  
                    No puedes fusionar, eliminar ni modificar frases ni palabras.

                    La suma de todos los textos de los bloques, en orden, debe ser EXACTAMENTE igual a la transcripción original.

                    **Si omites, repites o reordenas una sola palabra, la segmentación es inválida.**

                    Si no puedes segmentar sin dejar palabras fuera, haz bloques más grandes, pero NUNCA elimines palabras.


                    Devuélveme el resultado en formato JSON con la siguiente estructura:

                    {{
                    "nombre de funcionalidad": [
                        "texto perteneciente a la funcionalidad 1"
                    ],
                    "otra funcionalidad": [
                        "texto perteneciente a la funcionalidad 2"
                    ]
                    ...
                    }}

                    Por ejemplo, para la transcripción:  
                    'Abre el menú. Luego haz clic en opciones. Ahora cambia el nombre.'  
                    Podrías segmentar:
                    {{
                    "Abrir menú": ["Abre el menú."],
                    "Entrar en opciones": ["Luego haz clic en opciones."],
                    "Cambiar nombre": ["Ahora cambia el nombre."]
                    }}

                    Pero si no puedes segmentar bien sin omitir palabras, pon todo en un solo bloque, pero NUNCA omitas nada.


                    Intenta hacer los cortes de forma que segmente bien cada parte, y que un segmento no tenga distintas funcionalidades, para ello usa el contexto, para entender las distintas funcionalidades y separar bien.
                    En los nombres de funcionalidad no incluyas nada que no sean letras.
                    No incluyas ningún comentario adicional, solo el JSON de salida. 
                    
                    Aquí está la transcripción:

                    {transcription}
                    """
                }
            ],
            temperature=0.7
        )
        # Intenta parsear la respuesta a JSON
        content = response.choices[0].message.content
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Si hay errores, intenta extraer solo el JSON entre llaves
            start = content.find("{")
            end = content.rfind("}") + 1
            json_block = content[start:end]
            return json.loads(json_block)

    except Exception as e:
        print("❌ Error while calling API: ", e)
        return {}