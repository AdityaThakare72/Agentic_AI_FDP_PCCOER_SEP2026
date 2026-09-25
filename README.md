# Research & Quiz Generator

An AI agent that researches a topic on the web, writes study notes, pauses for a
teacher to review them, and then generates a multiple-choice quiz.
Built with LangGraph, Gemini and Tavily, with a Streamlit front end.

## How it works

```
START -> planner -> researcher -> note_writer -> teacher_review --approved--> quiz_generator -> END
                                      ^                |
                                      +---changes------+
```

- **planner** - splits the topic into 3 focused sub-questions (structured output)
- **researcher** - runs one Tavily web search per sub-question (plain Python, no LLM)
- **note_writer** - writes study notes from the research only, with sources
- **teacher_review** - pauses the graph with `interrupt()` until a human approves or asks for changes
- **quiz_generator** - creates the quiz as structured output (question, 4 options, answer, explanation)

## Project structure

```
research-quiz-agent/
  requirements.txt      exact library versions
  .env.example          template for your API keys (copy to .env)
  check_setup.py        run this first to confirm everything works
  run_cli.py            run the agent in the terminal (steps 1-4)
  app.py                the Streamlit app (connected in step 5)
  agent/
    llm.py              creates the Gemini model           (ready)
    schemas.py          Pydantic output shapes             (ready)
    prompts.py          prompt templates                   (ready)
    tools.py            Tavily search helpers              (ready)
    graph.py            the LangGraph agent                (built live, steps 1-4)
```

## Setup

Follow the setup guide document shared with you. In short, from this folder:

```
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
copy .env.example .env        (then paste your keys into .env)
python check_setup.py
```

## Running

```
python run_cli.py                  # terminal version, works from step 1
python -m streamlit run app.py     # web app, fully working after step 5
```

## Build steps (live session)

| Step | What we add | File |
|------|-------------|------|
| 1 | State + planner node | agent/graph.py |
| 2 | Researcher node (Tavily) | agent/graph.py |
| 3 | Note writer + quiz generator | agent/graph.py |
| 4 | Teacher review with interrupt() + checkpointer | agent/graph.py |
| 5 | Connect the Streamlit page to the graph | app.py |

## Fell behind?

After each step, the finished file for that step is shared in the group.
Open it, select all (Ctrl + A), copy, paste it over everything in your file
(`agent/graph.py` for steps 1-4, `app.py` for step 5), save, and carry on.

## Taking it further

- replace `InMemorySaver` with a SQLite or Postgres checkpointer so paused reviews survive a restart
- let the teacher edit the notes directly instead of only giving feedback
- add a difficulty setting per question, or export the quiz to a file
