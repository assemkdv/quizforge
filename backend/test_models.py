"""Tests for the Pydantic models in models.py.

These are some of the most important tests in the project: they prove
that bad input (from the user) and bad output (from the LLM) both get
rejected before they can cause problems elsewhere in the app.
"""

import pytest
from pydantic import ValidationError

from models import QuizQuestion, QuizRequest


def test_valid_quiz_request_is_accepted():
    request = QuizRequest(notes="A relation is reflexive if...", question_count=5)
    assert request.notes == "A relation is reflexive if..."
    assert request.question_count == 5


def test_empty_notes_are_rejected():
    with pytest.raises(ValidationError):
        QuizRequest(notes="", question_count=5)


def test_whitespace_only_notes_are_rejected():
    with pytest.raises(ValidationError):
        QuizRequest(notes="   ", question_count=5)


@pytest.mark.parametrize("question_count", [0, -1, 11, 100])
def test_invalid_question_count_is_rejected(question_count):
    with pytest.raises(ValidationError):
        QuizRequest(notes="Some notes", question_count=question_count)


def test_valid_quiz_question_is_accepted():
    question = QuizQuestion(
        question="Which property requires (a, a) to belong to R?",
        options=["Reflexive", "Symmetric", "Transitive", "Antisymmetric"],
        correct_answer="Reflexive",
    )
    assert question.correct_answer == "Reflexive"


def test_question_without_exactly_four_options_is_rejected():
    with pytest.raises(ValidationError):
        QuizQuestion(
            question="Which property requires (a, a) to belong to R?",
            options=["Reflexive", "Symmetric", "Transitive"],  # only 3
            correct_answer="Reflexive",
        )


def test_correct_answer_not_in_options_is_rejected():
    with pytest.raises(ValidationError):
        QuizQuestion(
            question="Which property requires (a, a) to belong to R?",
            options=["Reflexive", "Symmetric", "Transitive", "Antisymmetric"],
            correct_answer="Not one of the options",
        )
