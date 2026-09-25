"""
Research & Quiz Generator - Streamlit app.

Checkpoint: STEP 5 - the page is connected to the LangGraph agent.

Run with:
    python -m streamlit run app.py
"""

import uuid

import streamlit as st
from langgraph.types import Command

from agent.graph import build_graph

st.set_page_config(page_title="Research & Quiz Generator", layout="wide")

# friendly names for each node, shown while the agent works
NODE_LABELS = {
    "planner": "Planned the research",
    "researcher": "Searched the web",
    "note_writer": "Wrote the study notes",
    "teacher_review": "Recorded the teacher's decision",
    "quiz_generator": "Generated the quiz",
}


# ===============================================================
# Pre-written display helpers.
# These only draw things on the page. They know nothing about LangGraph.
# ===============================================================

def render_sidebar():
    """Inputs for a new quiz. Returns the values and whether Generate was clicked."""
    with st.sidebar:
        st.header("New quiz")
        topic = st.text_input("Topic", value="Photosynthesis")
        level = st.selectbox("Level", ["beginner", "intermediate", "advanced"])
        num_questions = st.slider("Number of questions", min_value=3, max_value=10, value=5)
        clicked = st.button("Generate", type="primary", width="stretch")
    return topic, level, num_questions, clicked


def render_welcome():
    st.markdown(
        "Enter a topic in the sidebar and click **Generate**. The agent will plan the research, "
        "search the web, write study notes, and pause for you to review them before it creates a quiz."
    )


def render_review(values: dict):
    """Show the notes for review. Returns ("approve" | "revise" | None, feedback)."""
    st.subheader("Review the study notes")
    st.caption("The agent is paused. Approve the notes to create the quiz, or ask for changes.")

    with st.expander("Research plan"):
        for question in values.get("sub_questions", []):
            st.markdown(f"- {question}")

    research = values.get("research", [])
    with st.expander(f"Sources ({len(research)})"):
        for finding in research:
            st.markdown(f"- [{finding['title']}]({finding['url']})")

    st.markdown(values.get("notes", ""))
    st.divider()

    feedback = st.text_area("What should change? (only needed if you are not approving)")
    left, right = st.columns(2)
    approve = left.button("Approve and create quiz", type="primary", width="stretch")
    revise = right.button("Rewrite with my changes", width="stretch")

    if approve:
        return "approve", ""
    if revise:
        if not feedback.strip():
            st.warning("Write what should change first, then click rewrite.")
            return None, ""
        return "revise", feedback
    return None, ""


def render_quiz(values: dict, key_suffix: str):
    """Show the quiz as a form, then score it when submitted."""
    quiz = values.get("quiz", [])
    st.subheader(f"Quiz: {values.get('topic', '')}")

    with st.expander("Study notes"):
        st.markdown(values.get("notes", ""))

    with st.form(key=f"quiz_form_{key_suffix}"):
        choices = []
        for number, item in enumerate(quiz, start=1):
            choice = st.radio(
                f"Q{number}. {item['question']}",
                item["options"],
                index=None,
                key=f"q{number}_{key_suffix}",
            )
            choices.append(choice)
        submitted = st.form_submit_button("Submit answers", type="primary")

    if submitted:
        score = 0
        for number, (item, choice) in enumerate(zip(quiz, choices), start=1):
            # guard against the model returning an index outside the options list
            answer_index = min(max(item["answer_index"], 0), len(item["options"]) - 1)
            correct = item["options"][answer_index]
            if choice == correct:
                score += 1
                st.success(f"Q{number}: correct. {item['explanation']}")
            elif choice is None:
                st.warning(f"Q{number}: not answered. The answer is: {correct}. {item['explanation']}")
            else:
                st.error(f"Q{number}: you chose \"{choice}\", the answer is \"{correct}\". {item['explanation']}")
        st.metric("Score", f"{score} / {len(quiz)}")


# ===============================================================
# STEP 5: connecting the page to the agent.
# ===============================================================

# Streamlit reruns this whole file on every click. cache_resource builds the
# graph once and reuses it, so the checkpointer (and any paused run inside it)
# survives between clicks.
@st.cache_resource
def load_graph():
    return build_graph()


graph = load_graph()

# session_state is the only thing Streamlit keeps between reruns for this user
if "stage" not in st.session_state:
    st.session_state.stage = "start"      # start -> review -> quiz
    st.session_state.thread_id = None


def get_config():
    # the thread_id tells the checkpointer which paused run we mean
    return {"configurable": {"thread_id": st.session_state.thread_id}}


def run_graph(graph_input):
    """Run the graph until it finishes or pauses, showing progress as nodes finish."""
    with st.status("The agent is working...", expanded=True) as status:
        try:
            for update in graph.stream(graph_input, get_config(), stream_mode="updates"):
                for node_name in update:
                    if node_name != "__interrupt__":
                        status.write(NODE_LABELS.get(node_name, node_name))
        except Exception as error:
            status.update(label="Something went wrong", state="error")
            st.error(f"The agent stopped with an error: {error}")
            st.stop()
        status.update(label="Done", state="complete", expanded=False)

    # if the graph still has a next node, it is paused waiting for review
    snapshot = graph.get_state(get_config())
    st.session_state.stage = "review" if snapshot.next else "quiz"


st.title("Research & Quiz Generator")
topic, level, num_questions, generate_clicked = render_sidebar()

if generate_clicked:
    # a fresh thread_id for every new quiz, so runs never mix
    st.session_state.thread_id = str(uuid.uuid4())
    run_graph({"topic": topic, "level": level, "num_questions": num_questions})
    st.rerun()

if st.session_state.stage == "start":
    render_welcome()

else:
    values = graph.get_state(get_config()).values

    if st.session_state.stage == "review":
        action, feedback = render_review(values)
        if action == "approve":
            run_graph(Command(resume={"approved": True}))
            st.rerun()
        elif action == "revise":
            run_graph(Command(resume={"approved": False, "feedback": feedback}))
            st.rerun()

    elif st.session_state.stage == "quiz":
        render_quiz(values, key_suffix=st.session_state.thread_id)
