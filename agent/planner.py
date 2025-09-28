class PlannerAgent:
    def __init__(self, api_key):
        self.api_key = api_key

    def plan(self, user_request: str):
        # Simple placeholder plan
        return f"""Project Plan: {user_request}

Objective: Build a simple, user-friendly application.
Technologies: HTML, CSS, JavaScript
Phases:
1. Planning and Design
2. Development
3. Deployment
4. Documentation and Feedback"""
