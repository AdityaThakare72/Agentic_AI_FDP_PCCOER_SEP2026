"""
Run the agent graph from the terminal, and print what every node produced.

Works at every step of the build: it simply shows whichever nodes exist.
From step 4 onwards, it also pauses for you to approve or reject the notes.

Usage:
    python run_cli.py
"""

import uuid

from langgraph.types import Command

from agent.graph import build_graph


def show_node_output(node_name: str, output: dict):
    """Print a readable summary of what one node returned."""
    print(f"\n========== {node_name} ==========")

    if "sub_questions" in output:
        for number, question in enumerate(output["sub_questions"], start=1):
            print(f"{number}. {question}")

    if "research" in output:
        print(f"{len(output['research'])} search results collected:")
        for finding in output["research"]:
            print(f"  - {finding['title']}  ({finding['url']})")

    if "notes" in output:
        print(output["notes"])

    if "approved" in output:
        print("approved" if output["approved"] else f"changes requested: {output.get('feedback', '')}")

    if "quiz" in output:
        for number, item in enumerate(output["quiz"], start=1):
            print(f"\nQ{number}. {item['question']}")
            for index, option in enumerate(item["options"]):
                marker = "*" if index == item["answer_index"] else " "
                print(f"   {marker} {index}) {option}")
            print(f"   why: {item['explanation']}")


def main():
    graph = build_graph()

    # one thread_id = one run; the checkpointer uses it to find a paused run again
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    topic = input("Topic (press Enter for 'Photosynthesis'): ").strip() or "Photosynthesis"
    level = input("Level - beginner / intermediate / advanced (Enter for beginner): ").strip() or "beginner"

    graph_input = {"topic": topic, "level": level, "num_questions": 5}

    while True:
        paused = False

        # stream_mode="updates" gives us one update per finished node
        for update in graph.stream(graph_input, config, stream_mode="updates"):
            for node_name, output in update.items():
                if node_name == "__interrupt__":
                    paused = True
                else:
                    show_node_output(node_name, output or {})

        if not paused:
            break

        # the graph is paused inside teacher_review, waiting for our decision
        answer = input("\nApprove these notes? (y/n): ").strip().lower()
        if answer == "y":
            graph_input = Command(resume={"approved": True})
        else:
            feedback = input("What should change? ").strip()
            graph_input = Command(resume={"approved": False, "feedback": feedback})

    print("\nDone.")


if __name__ == "__main__":
    main()
