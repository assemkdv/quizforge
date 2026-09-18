"""Tests for quiz_generator.py.

The only thing worth testing here is our own logic around the LLM call —
not Groq itself. The Groq client is mocked in every test, so these run
instantly, make no real network call, and never touch the real API key.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

import quiz_generator


def _mock_groq_response(payload: dict) -> MagicMock:
    """Build a fake Groq response shaped like the real SDK's return value."""
    response = MagicMock()
    response.choices[0].message.content = json.dumps(payload)
    return response


def test_generate_quiz_returns_validated_quiz(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    payload = {
        "questions": [
            {"question": "Q1?", "options": ["A", "B", "C", "D"], "correct_answer": "A"}
        ]
    }

    with patch("quiz_generator.Groq") as MockGroq:
        MockGroq.return_value.chat.completions.create.return_value = (
            _mock_groq_response(payload)
        )
        quiz = quiz_generator.generate_quiz("some notes", 1)

    assert len(quiz.questions) == 1
    assert quiz.questions[0].correct_answer == "A"


def test_wrong_number_of_questions_is_rejected(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    # 3 questions were requested, but the mocked LLM only returns 1.
    payload = {
        "questions": [
            {"question": "Q1?", "options": ["A", "B", "C", "D"], "correct_answer": "A"}
        ]
    }

    with patch("quiz_generator.Groq") as MockGroq:
        MockGroq.return_value.chat.completions.create.return_value = (
            _mock_groq_response(payload)
        )
        with pytest.raises(ValueError):
            quiz_generator.generate_quiz("some notes", 3)


def test_missing_api_key_raises_runtime_error(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        quiz_generator.generate_quiz("some notes", 1)
