"""LLM integration for QuizForge.

This is the only module that talks to the LLM. Its one job: take the
user's notes and desired question count, ask the LLM to generate a quiz,
and turn the response into a validated QuizResponse using the Pydantic
models from models.py. Nothing else in the backend calls the LLM directly.
"""

import json
import os

from dotenv import load_dotenv
from groq import Groq

from models import QuizResponse

# Load variables from backend/.env (e.g. LLM_API_KEY) into the process
# environment. This runs once, when the module is first imported.
load_dotenv()

# Model hosted on Groq used for quiz generation. Qwen3.8 27B is available
# on this account, is capable enough to write plausible wrong answers, and
# supports Groq's JSON output mode (used below).
MODEL_NAME = "qwen/qwen3.8-27b"


def generate_quiz(notes: str, question_count: int) -> QuizResponse:
    """Ask the LLM for a quiz and return it as a validated QuizResponse.

    Raises an exception if anything goes wrong: a missing API key
    (RuntimeError), a Groq API failure, invalid JSON (json.JSONDecodeError),
    a quiz that fails Pydantic validation, or one that returns the wrong
    number of questions (ValueError). main.py is responsible for turning
    any of these into a clean HTTP error for the frontend.
    """
    api_key = os.environ.get("LLM_API_KEY")
    if not api_key:
        raise RuntimeError("LLM_API_KEY is not configured")

    client = Groq(api_key=api_key)

    prompt = build_quiz_prompt(notes, question_count)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
        # Ask Groq to guarantee syntactically valid JSON output. This
        # model doesn't support strict JSON-schema enforcement, but JSON
        # object mode is supported and cuts down "model added prose
        # around the JSON" failures. Pydantic (below) is still the real
        # validation step — this just makes json.loads() more reliable.
        response_format={"type": "json_object"},
    )

    raw_text = response.choices[0].message.content
    quiz_data = json.loads(raw_text)
    quiz = QuizResponse(**quiz_data)

    if len(quiz.questions) != question_count:
        raise ValueError(
            f"Expected {question_count} questions from the LLM, "
            f"got {len(quiz.questions)}"
        )

    return quiz


def build_quiz_prompt(notes: str, question_count: int) -> str:
    """Build the instruction prompt sent to the LLM."""
    return f"""You are generating a multiple-choice quiz for a student, based strictly on the study notes provided below.

Rules:
- Use ONLY information contained in the notes below. Do not use outside knowledge.
- Generate exactly {question_count} question(s).
- Each question must have exactly 4 answer options.
- Exactly 1 of the 4 options must be correct.
- The 3 incorrect options should be plausible, not obviously wrong.
- Do not include any explanations, headers, markdown, or extra prose.
- Respond with ONLY valid JSON, in exactly this shape, and nothing else:

{{
  "questions": [
    {{
      "question": "...",
      "options": ["...", "...", "...", "..."],
      "correct_answer": "..."
    }}
  ]
}}

Study notes:
\"\"\"
{notes}
\"\"\"
"""
