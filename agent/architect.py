from langchain_openai import ChatOpenAI

class ArchitectAgent:
    def __init__(self, api_key):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=api_key)

    def design(self, project_plan: str):
        prompt = f"""
        You are an architect. Break down the project plan into tasks for each file.
        Return output in strict JSON format as a list of objects:
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
        return response
