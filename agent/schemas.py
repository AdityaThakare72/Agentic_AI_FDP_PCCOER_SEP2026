"""
Pydantic schemas that force Gemini to return structured data instead of free text.

This is the same idea as the RouterDecision in the multi-agent session:
with_structured_output(SomeSchema) makes the model's answer match the shape
we define here, so our code gets back a clean Python object, not a paragraph
we would have to parse.
"""

from pydantic import BaseModel, Field


class ResearchPlan(BaseModel):
    """What the planner node produces."""

    sub_questions: list[str] = Field(
        description="Exactly 3 focused questions that together cover the topic at the requested level."
    )


class QuizQuestion(BaseModel):
    """One multiple-choice question."""

    question: str = Field(description="The question text.")
    options: list[str] = Field(description="Exactly 4 answer options.")
    answer_index: int = Field(description="Position of the correct option in the list, from 0 to 3.")
    explanation: str = Field(description="One or two sentences explaining why the answer is correct.")


class Quiz(BaseModel):
    """What the quiz generator node produces."""

    questions: list[QuizQuestion]
