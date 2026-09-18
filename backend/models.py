"""Pydantic models for the QuizForge API.

These models define the shape of data that flows in and out of
POST /api/quiz. FastAPI uses them to validate the incoming request and
to shape the outgoing response — anything that doesn't match gets
rejected before it reaches (or leaves) our own code.
"""

from pydantic import BaseModel, field_validator, model_validator


class QuizRequest(BaseModel):
    """What the frontend sends when asking for a quiz."""

    notes: str
    question_count: int

    @field_validator("notes")
    @classmethod
    def notes_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("notes must not be empty")
        return value

    @field_validator("question_count")
    @classmethod
    def question_count_must_be_reasonable(cls, value: int) -> int:
        if not (1 <= value <= 10):
            raise ValueError("question_count must be between 1 and 10")
        return value


class QuizQuestion(BaseModel):
    """A single multiple-choice question."""

    question: str
    options: list[str]
    correct_answer: str

    @field_validator("question")
    @classmethod
    def question_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("question text must not be empty")
        return value

    @field_validator("options")
    @classmethod
    def must_have_exactly_four_options(cls, value: list[str]) -> list[str]:
        if len(value) != 4:
            raise ValueError("a question must have exactly four options")
        return value

    @model_validator(mode="after")
    def correct_answer_must_be_one_of_the_options(self) -> "QuizQuestion":
        if self.correct_answer not in self.options:
            raise ValueError("correct_answer must be one of the options")
        return self


class QuizResponse(BaseModel):
    """What the backend sends back: the full generated quiz."""

    questions: list[QuizQuestion]
