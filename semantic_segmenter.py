import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def segmenter(transcription_path: str, context: str, model="gpt-4") -> dict:
    with open(transcription_path, "r", encoding="utf-8") as file:
        transcription = file.read()
        
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

Devuélveme el resultado en formato JSON con la siguiente estructura:

{{
"nombre_de_funcionalidad": [
    "texto perteneciente a la funcionalidad 1"
],
"otra_funcionalidad": [
    "texto perteneciente a la funcionalidad 2"
]
...
}}

Intenta hacer los cortes de forma que segmente bien cada parte, y que un segmento no tenga distintas funcionalidades, para ello usa el contexto, para entender las distintas funcionalidades y separar bien.
En los nombres de funcionalidad no incluyas nada que no sean letras, no incluyas por ejemplo "-".
No incluyas ningún comentario adicional, solo el JSON de salida. Aquí está la transcripción:

{transcription}
"""
                }
            ],
            temperature=0.7
        )
        content = response.choices[0].message.content
        try:
            blocks = json.loads(content)
        except json.JSONDecodeError:
            print("⚠️ JSON malformado. Intentando extraer solo las llaves...")
            start = content.find("{")
            end = content.rfind("}") + 1
            json_block = content[start:end]
            blocks = json.loads(json_block)

        with open("semantic_blocks.json", "w", encoding="utf-8") as f:
            json.dump(blocks, f, indent=2, ensure_ascii=False)

        print("✅ Bloques temáticos guardados en semantic_blocks.json")
        return blocks

    except Exception as e:
        print("❌ Error al llamar a la API:", e)
        return {}

if __name__ == "__main__":
    with open("context.json", "r", encoding="utf-8") as f:
        context_data = json.load(f)
    context_str = json.dumps(context_data, ensure_ascii=False)
    segmenter("transcription.txt", context_str)