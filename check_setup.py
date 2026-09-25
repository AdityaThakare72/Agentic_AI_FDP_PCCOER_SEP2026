"""
Checks that your environment is ready for the capstone session.

Run it from the project folder, with your virtual environment active:
    python check_setup.py

Every line should say OK. If something says FAIL, the message tells you what to do,
and the setup guide has more detail for each problem.
"""

import os
import sys

problems = 0


def ok(message):
    print(f"  OK    {message}")


def fail(message, fix):
    global problems
    problems += 1
    print(f"  FAIL  {message}")
    print(f"        fix: {fix}")


print("\n0. Project folder")
if os.path.exists("app.py") and os.path.isdir("agent"):
    ok(f"running from the project folder ({os.getcwd()})")
else:
    fail(
        f"this does not look like the project folder ({os.getcwd()})",
        "cd into the research-quiz-agent folder (the one containing app.py) and run this again",
    )

print("\n1. Python")
version = sys.version_info
if version >= (3, 10):
    ok(f"Python {version.major}.{version.minor}.{version.micro}")
else:
    fail(f"Python {version.major}.{version.minor} is too old", "install Python 3.12 from python.org")

if sys.prefix != sys.base_prefix:
    ok(f"running inside a virtual environment ({sys.prefix})")
else:
    fail(
        "not running inside a virtual environment",
        "activate it first: .venv\\Scripts\\Activate.ps1 (PowerShell) or .venv\\Scripts\\activate.bat (Command Prompt)",
    )

print("\n2. Libraries")
for module_name in ["langgraph", "langchain", "langchain_google_genai", "langchain_tavily", "streamlit", "dotenv"]:
    try:
        __import__(module_name)
        ok(module_name)
    except ImportError:
        fail(f"{module_name} is not installed", "python -m pip install -r requirements.txt")

print("\n3. API keys")
if not os.path.exists(".env") and os.path.exists(".env.txt"):
    fail(
        "found .env.txt instead of .env (Windows hid the .txt extension)",
        "rename it in the terminal: Rename-Item .env.txt .env",
    )
elif not os.path.exists(".env"):
    fail(
        "no .env file in this folder",
        "copy .env.example to .env and paste your keys in (check it is not named .env.txt)",
    )
else:
    from dotenv import load_dotenv

    load_dotenv()
    for key_name in ["GOOGLE_API_KEY", "TAVILY_API_KEY"]:
        value = os.getenv(key_name, "").strip()
        if not value or value.startswith("paste-your"):
            fail(f"{key_name} is missing", f"open .env and paste your real {key_name} after the = sign")
        else:
            ok(f"{key_name} found (ends with ...{value[-4:]})")

print("\n4. Live API calls")
if problems:
    print("  skipped - fix the problems above first")
else:
    try:
        from agent.llm import get_model

        reply = get_model().invoke("Reply with just the word: ready")
        ok(f"Gemini replied: {reply.text.strip()[:40]}")
    except Exception as error:
        fail(f"Gemini call failed: {error}", "check GOOGLE_API_KEY in .env, and your internet connection")

    try:
        from agent.tools import research_web

        results = research_web("what is LangGraph", max_results=1)
        if results:
            ok(f"Tavily search returned: {results[0]['title'][:60]}")
        else:
            fail("Tavily returned no results", "check TAVILY_API_KEY in .env")
    except Exception as error:
        fail(f"Tavily call failed: {error}", "check TAVILY_API_KEY in .env, and your internet connection")

print()
if problems:
    print(f"{problems} problem(s) found. Fix them and run this script again.")
else:
    print("All good. You are ready for the session.")
