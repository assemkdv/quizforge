"""FastAPI application for QuizForge.

Exposes a single endpoint, POST /api/quiz, which sends the user's study
notes to an LLM (via quiz_generator.py) and returns a validated quiz.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import quiz_generator
from models import QuizRequest, QuizResponse

app = FastAPI(title="QuizForge API")

# The frontend is served from a different origin than this API during
# local development (e.g. http://localhost:5500 vs http://127.0.0.1:8000),
# so the browser blocks fetch() responses unless we explicitly allow it.
# We only allow the specific local dev origins the frontend runs on —
# not "*" — since that would let any website call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)


@app.post("/api/quiz", response_model=QuizResponse)
def generate_quiz(request: QuizRequest) -> QuizResponse:
    """Generate a quiz from the given study notes using the LLM.

    Two clear error paths, both without leaking internal details:
    - RuntimeError means the server itself is misconfigured (e.g. no
      LLM_API_KEY set) — that's not something the user can fix by
      retrying, so it gets a 500.
    - Anything else (a Groq API error, invalid JSON from the LLM, a quiz
      that fails Pydantic validation, or the wrong number of questions)
      means this specific generation attempt failed — that's a 502, and
      retrying may well work.
    """
    try:
        return quiz_generator.generate_quiz(
            notes=request.notes,
            question_count=request.question_count,
        )
    except RuntimeError as error:
        raise HTTPException(
            status_code=500,
            detail="The server is not configured correctly. Please contact the site owner.",
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail="Could not generate the quiz. Please try again.",
        ) from error
