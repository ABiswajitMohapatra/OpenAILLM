from langchain_openai import ChatOpenAI
import json
import re

class ArchitectAgent:
    def __init__(self, api_key):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=api_key)

    def design(self, project_plan: str):
        prompt = f"""
        You are an architect. Break down the project plan into tasks for each file.
        Return output in strict JSON format only — a list of objects with "filename" and "task".
        Do NOT add any explanation or text outside of JSON.
        
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

        # Get response from LLM
        response = self.llm.invoke(prompt).content

        # Extract JSON using regex in case the LLM adds extra text
        json_match = re.search(r'(\[.*\])', response, re.DOTALL)
        if json_match:
            try:
                breakdown_json = json.loads(json_match.group(1))
                return breakdown_json
            except json.JSONDecodeError:
                raise ValueError("LLM returned invalid JSON")
        else:
            raise ValueError("LLM output does not contain valid JSON")
