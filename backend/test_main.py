"""Tests for the POST /api/quiz endpoint in main.py.

These tests never call the real Groq API — quiz_generator.generate_quiz
is mocked, so they run instantly and don't depend on network access or a
real API key. What's actually being tested is main.py's own job: turning
a successful or failed generation into the right HTTP response.
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app
from models import QuizQuestion, QuizResponse

client = TestClient(app)


def test_api_quiz_returns_expected_response_when_generation_succeeds():
    fake_quiz = QuizResponse(
        questions=[
            QuizQuestion(
                question="Q1?",
                options=["A", "B", "C", "D"],
                correct_answer="A",
            )
        ]
    )

    with patch("quiz_generator.generate_quiz", return_value=fake_quiz):
        response = client.post(
            "/api/quiz", json={"notes": "some notes", "question_count": 1}
        )

    assert response.status_code == 200
    assert response.json() == fake_quiz.model_dump()


def test_api_quiz_returns_clean_error_when_generation_fails():
    with patch("quiz_generator.generate_quiz", side_effect=Exception("boom")):
        response = client.post(
            "/api/quiz", json={"notes": "some notes", "question_count": 1}
        )

    assert response.status_code == 502
    assert response.json() == {
        "detail": "Could not generate the quiz. Please try again."
    }
