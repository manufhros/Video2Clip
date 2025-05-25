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
                    Starting with the following tutorial transcript, you need to divide the transcript into sections, leaving no words out (it's like making cuts in the original text). These cuts should be thematically related, meaning sections into which a tutorial can be divided, for example: "Change Name," "Change Image," etc.
                    Additionally, for this tutorial, we have context for the tool we're using. Use this information to make the cuts more precise. The context is as follows:
                    {context}

                    **NO WORDS MAY BE OMITTED.**
                    Each word in the transcript MUST appear ONLY ONCE in one of the blocks.
                    You may not change the order of the words.
                    You may not merge, delete, or modify phrases or words.

                    The sum of all the texts in the blocks, in order, must be EXACTLY the same as the original transcription.

                    **If you omit, repeat, or reorder a single word, the segmentation is invalid.**

                    If you can't segment without leaving out words, make larger blocks, but NEVER delete words.

                    Return the result in JSON format with the following structure:

                    {{
                    "feature name": [
                        "text belonging to feature 1"
                    ],
                    "other feature": [
                        "text belonging to feature 2"
                    ]
                    ...
                    }}

                    For example, for transcription:
                    'Open the menu. Then click Options. Now change the name.'
                    You could segment:
                    {{
                    "Open Menu": ["Open the menu."],
                    "Enter Options": ["Then click Options."],
                    "Rename": ["Now change the name."]
                    }}

                    But if you can't segment well without omitting words, put everything in a single block, but NEVER omit anything.

                    Try to make the cuts so that each part is segmented well, and that one segment doesn't have different functionalities. To do this, use context to understand the different functionalities and separate them well.
                    Don't include anything other than letters in feature names.
                    Don't include any additional comments, just the output JSON.

                    Here's the transcription:

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