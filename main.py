import os
from agent.planner import PlannerAgent
from agent.architect import ArchitectAgent
from agent.coder import CoderAgent
import http.server, socketserver, threading, webbrowser

api_key = os.environ.get("OPENAI_API_KEY")

def save_generated_files(files, project_name):
    os.makedirs(project_name, exist_ok=True)
    for f in files:
        with open(os.path.join(project_name, f['filename']), 'w', encoding='utf-8') as fp:
            fp.write(f['content'])
    return os.path.abspath(project_name)

def serve_website(folder_path, port=8000):
    os.chdir(folder_path)
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), handler)
    threading.Thread(target=lambda: webbrowser.open(f"http://localhost:{port}")).start()
    httpd.serve_forever()

def main():
    if not api_key:
        print("❌ OPENAI_API_KEY not found. Please set it in environment variables.")
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
    result = coder.implement(breakdown, plan)
    print(result)

    project_folder = save_generated_files(result, "lovable_ai_site")
    print(f"\n✅ Website generated at {project_folder}")
    print("🌐 Launching live preview in your browser...")
    serve_website(project_folder)

if __name__ == "__main__":
    main()
