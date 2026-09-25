"""
Research & Quiz Generator - the agent graph.

We build this file together, live, in 4 steps:
  Step 1: the state and the planner node
  Step 2: the researcher node (web search with Tavily)
  Step 3: the note writer and quiz generator nodes
  Step 4: teacher review with interrupt() and a checkpointer

Fell behind or something broke? After each step, the finished graph.py for
that step is shared in the group. Open it, select all, copy, paste it over
everything in this file, save, and carry on.

Test it at any step with:
    python run_cli.py
"""

# Step 1 starts here

from typing import TypedDict
from urllib import response
from langgraph.graph import StateGraph, START, END
from matplotlib import text
from agent.llm import get_model
from agent.schemas import ResearchPlan, Quiz
from agent.prompts import PLANNER_PROMPT, NOTES_PROMPT, QUIZ_PROMPT
from agent.tools import research_web, format_research
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt

class QuizState(TypedDict):
    """The state of the quiz generator graph."""

    topic: str      # what the teacher asked for, e.g. "photosynthesis"
    level: str      # audience level, eg. beginner, intermediate, advanced
    num_questions: int  # how many questions the teacher wants in the quiz
    sub_questions: list[str]
    research: list[dict]  # search result: question, title, url, content
    notes: str  # the notes generated from the research
    quiz: list[dict] # final quiz
    feedback: str  # teacher feedback on the notes, if any
    approved: bool # did the teacher approve the notes, or request changes?

model = get_model(temperature=0.3)

def planner(state: QuizState):
    planner_llm = model.with_structured_output(ResearchPlan)
    prompt = PLANNER_PROMPT.format(topic=state["topic"], level=state["level"])
    plan = planner_llm.invoke(prompt)
    return {"sub_questions": plan.sub_questions}



# step 2

def researcher(state:QuizState):

    findings = []
    for question in state["sub_questions"]:
        for result in research_web(question, max_results=3):
            findings.append({
                "question": question, **result
            })

    return {"research": findings}




# step 3

def note_writer(state: QuizState):
    feedback_block = ""
    if state.get("feedback"):
        feedback_block = (
            "A teacher reviewed the notes and requested changes:\n"
            f"{state['feedback']}\n\n"
            "Please revise the notes to address this feedback fully."
        )


    prompt = NOTES_PROMPT.format(
        topic=state["topic"],
        level=state["level"],
        research=format_research(state["research"]),
        feedback_block=feedback_block,
    )

    response = model.invoke(prompt)
    return {"notes": response.text}

def teacher_review(state: QuizState):
    decision = interrupt({"notes": state["notes"]})
    return {
        "approved": decision.get("approved", False),
        "feedback": decision.get("feedback", ""),
    }

def route_after_review(state: QuizState):
    if state["approved"]:
        return "quiz_generator"
    else:
        return "note_writer"

def quiz_generator(state: QuizState):
    quiz_llm = model.with_structured_output(Quiz)
    prompt = QUIZ_PROMPT.format(
        num_questions=state["num_questions"],
        notes=state["notes"],
    )
    quiz = quiz_llm.invoke(prompt)
    # convert pydantic objects to plain dicts so they are easy to store and display
    return {"quiz": [question.model_dump() for question in quiz.questions]}



# build the final graph

def build_graph():
    builder = StateGraph(QuizState)

    builder.add_node("planner", planner)
    builder.add_node("researcher", researcher)
    builder.add_node("note_writer", note_writer)
    builder.add_node("quiz_generator", quiz_generator)
    builder.add_node("teacher_review", teacher_review)

    builder.add_edge(START, "planner")
    builder.add_edge("planner", "researcher")
    builder.add_edge("researcher", "note_writer")
    builder.add_edge("note_writer", "teacher_review")

    builder.add_conditional_edges("teacher_review",
                                   route_after_review,
                                   ["quiz_generator", "note_writer"])
    builder.add_edge("quiz_generator", END)


    return builder.compile(checkpointer=InMemorySaver())

