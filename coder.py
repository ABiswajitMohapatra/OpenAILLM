import os
import json
from langchain_openai import ChatOpenAI

class CoderAgent:
    def __init__(self, api_key):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=api_key)

    def implement(self, breakdown: str, base_path="resources"):
        try:
            tasks = json.loads(breakdown)
        except json.JSONDecodeError:
            return "❌ Architect output is not valid JSON."

        results = []
        for task in tasks:
            filename = os.path.join(base_path, task["filename"])
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            prompt = f"Write complete code for: {task['task']}"
            code = self.llm.invoke(prompt).content

            with open(filename, "w") as f:
                f.write(code)

            results.append(f"✅ {filename} created.")

        return "\n".join(results)
