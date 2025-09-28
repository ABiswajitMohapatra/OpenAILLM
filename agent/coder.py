from langchain_openai import ChatOpenAI

class CoderAgent:
    def __init__(self, api_key):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=api_key)

    def implement(self, breakdown, project_plan: str):
        generated_files = []
        for file in breakdown:
            prompt = f"""
You are a senior developer. Write the complete code for {file['filename']} for the following project:
{project_plan}

File purpose: {file['task']}

Return ONLY the file content, do not include explanations or code blocks.
"""
            content = self.llm.invoke(prompt).content.strip()
            generated_files.append({
                "filename": file['filename'],
                "content": content
            })
        return generated_files
