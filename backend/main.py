"""FastAPI application for QuizForge.

Exposes a single endpoint, POST /api/quiz, which will eventually call an
LLM to generate a quiz from study notes. For now (Phase 2), it returns a
fixed, hardcoded quiz so we can verify the request/response shape and
test the API through /docs before any LLM integration exists.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import QuizQuestion, QuizRequest, QuizResponse

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
    """Return a quiz for the given study notes.

    Phase 2 note: this ignores `request.notes` and `request.question_count`
    and always returns the same hardcoded quiz below. That's intentional —
    it lets us confirm the API contract (what a request/response looks
    like) works end-to-end before wiring up a real LLM call.
    """
    return QuizResponse(
        questions=[
            QuizQuestion(
                question="Which property requires (a, a) to belong to R?",
                options=["Reflexive", "Symmetric", "Transitive", "Antisymmetric"],
                correct_answer="Reflexive",
            ),
            QuizQuestion(
                question=(
                    "Which property requires that if (a, b) is in R, "
                    "then (b, a) is also in R?"
                ),
                options=["Reflexive", "Symmetric", "Transitive", "Antisymmetric"],
                correct_answer="Symmetric",
            ),
            QuizQuestion(
                question=(
                    "Which property requires that if (a, b) and (b, c) are "
                    "in R, then (a, c) is also in R?"
                ),
                options=["Reflexive", "Symmetric", "Transitive", "Antisymmetric"],
                correct_answer="Transitive",
            ),
        ]
    )
