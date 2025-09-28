import os
from agent.planner import PlannerAgent
from agent.architect import ArchitectAgent
from agent.coder import CoderAgent

# Get API key from environment variables (set in Streamlit Cloud Secrets)
api_key = os.environ.get("OPENAI_API_KEY")

def main():
    if not api_key:
        print("❌ OPENAI_API_KEY not found. Please set it in your Streamlit Cloud Secrets.")
        return

    user_request = input("🚀 Enter your project request: ")

    planner = PlannerAgent(api_key)
    architect = ArchitectAgent(api_key)
    coder = CoderAgent(api_key)

    print("\n📌 Generating project plan...")
    plan = planner.plan(user_request)
    print(plan)

    print("\n📌 Breaking down into files (JSON)...")
    breakdown = architect.design(plan)
    print(breakdown)

    print("\n📌 Writing code files...")
    result = coder.implement(breakdown)
    print(result)

if __name__ == "__main__":
    main()
