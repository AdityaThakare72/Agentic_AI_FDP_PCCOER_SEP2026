"""
Prompt templates for each LLM step.

These are plain Python strings with {placeholders}. Each node fills in the
placeholders with .format(...) before sending the prompt to the model.
Keeping prompts out of the graph code makes the graph easier to read,
and lets us tune wording without touching any logic.
"""

PLANNER_PROMPT = """You are planning research for a short piece of study material.

Topic: {topic}
Audience level: {level}

Break this topic into exactly 3 focused sub-questions. Together they should
cover what a {level} learner most needs to understand about the topic.
Each sub-question should work well as a web search query."""


NOTES_PROMPT = """You are writing study notes on "{topic}" for {level} learners.

Use ONLY the research provided below. Do not add facts that are not supported by it.

Structure the notes like this:
1. A two or three sentence introduction
2. Key concepts, each with a short heading and a clear explanation
3. One simple real-life example or analogy
4. A summary of 3 to 5 bullet points
5. A "Sources" section listing the URLs you actually used

Keep the notes under 600 words and use markdown formatting.

Research:
{research}

{feedback_block}"""


QUIZ_PROMPT = """Create {num_questions} multiple-choice questions based ONLY on the study notes below.

Rules:
- each question has exactly 4 options, and only one of them is correct
- answer_index is the position of the correct option (0, 1, 2 or 3)
- vary the position of the correct answer across questions
- mix easy and moderately challenging questions, no trick questions
- the explanation should say in one or two sentences why the answer is correct

Study notes:
{notes}"""
