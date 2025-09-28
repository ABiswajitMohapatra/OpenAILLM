import json
import re
from langchain_openai import ChatOpenAI

class ArchitectAgent:
    def __init__(self, api_key):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=api_key)

    def design(self, project_plan: str):
        prompt = f"""
        You are an architect. Break down the project plan into tasks for each file.
        Return output in strict JSON format only — a list of objects with "filename" and "task".
        Do NOT include explanations or code blocks (no ```json or ```).
        
        Example format:
        [
          {{
            "filename": "index.html",
            "task": "HTML structure for the app"
          }},
          {{
            "filename": "style.css",
            "task": "Styling for the app"
          }},
          {{
            "filename": "app.js",
            "task": "JavaScript logic"
          }}
        ]

        Project plan:
        {project_plan}
        """

        response = self.llm.invoke(prompt).content

        # Remove code block markers if present
        response = re.sub(r"```.*?```", "", response, flags=re.DOTALL).strip()

        # Decode escaped newlines and quotes if returned as string
        response = response.encode('utf-8').decode('unicode_escape')

        # Extract JSON array
        json_match = re.search(r'(\[.*\])', response, re.DOTALL)
        if json_match:
            try:
                breakdown_json = json.loads(json_match.group(1))
                return breakdown_json
            except json.JSONDecodeError as e:
                raise ValueError(f"LLM returned invalid JSON: {e}")
        else:
            raise ValueError("LLM output does not contain valid JSON")
