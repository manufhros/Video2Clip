import os
import json
import textwrap
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_context(transcription: str, model="gpt-4") -> str:
    prompt = textwrap.dedent(f"""
        You are an expert assistant in video tutorial analysis.

        You will be provided with a full transcript of a video tutorial.

        Your task is to analyze the content and extract a structured summary that describes the overall context of the tutorial. The result is returned in JSON format with the following properties:

        {{
          "tool_name": string,
          "tool_type": string,
          "goal_summary": string,
          "user_level": "beginner" | "intermediate" | "advanced",
          "main_entities": [string],
          "common_actions": [string],
          "functional_blocks": [string],
          "navigation_patterns": [string],
          "ui_elements": [string],
          "language": string
        }}
                             
        For "tool_name" it is possible that the transcription did not detect the name correctly, you should try to deduce it from the context and from known tools that have a similar name and allow you to do what is explained in the transcription, for example "Toogle Docs" is clearly "Google Docs".

        Please DO NOT add additional explanations or comments. Returns only the JSON object.

        Here is the transcript:
        {transcription}
    """)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an assistant who analyzes video tutorial transcripts to extract structured context."},
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
        print("❌ Error while calling API:", e)
        return {}