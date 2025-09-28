from langchain_openai import ChatOpenAI

class PlannerAgent:
    def __init__(self, api_key):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=api_key)

    def plan(self, request: str):
        prompt = f"You are a planner. Create a detailed project plan for: {request}"
        return self.llm.invoke(prompt).content
