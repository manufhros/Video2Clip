import os
import json
import textwrap
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_context(transcription: str, model="gpt-4") -> str:
    prompt = textwrap.dedent(f"""
        Eres un asistente experto en análisis de videotutoriales.

        Se te proporcionará una transcripción completa de un videotutorial.

        Tu tarea es analizar el contenido y extraer un resumen estructurado que describa el contexto general del tutorial. Devuelve el resultado en formato JSON con las siguientes propiedades:

        {{
          "tool_name": string,
          "tool_type": string,
          "goal_summary": string,
          "user_level": "principiante" | "intermedio" | "avanzado",
          "main_entities": [string],
          "common_actions": [string],
          "functional_blocks": [string],
          "navigation_patterns": [string],
          "ui_elements": [string],
          "language": string
        }}
                             
        Para "tool_name" es posible que la transcripción no haya detectado bien el nombre, debes de intentar deducirlo a partir del contexto y de las herramientas conocidas que tienen un nombre parecido y permiten hacer lo que explica en la transcripción, por ejemplo "Toogle Docs" es claramente "Google Docs".

        Por favor, NO añadas explicaciones adicionales ni comentarios. Devuelve solo el objeto JSON.

        Aquí está la transcripción:
        {transcription}
    """)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Eres un asistente que analiza transcripciones de videotutoriales para extraer contexto estructurado."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            start = content.find("{")
            end = content.rfind("}") + 1
            json_block = content[start:end]
            return json.loads(json_block)

    except Exception as e:
        print("❌ Error al llamar a la API:", e)
        return {}