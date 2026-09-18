"""FastAPI application for QuizForge.

Exposes a single endpoint, POST /api/quiz, which will eventually call an
LLM to generate a quiz from study notes. For now (Phase 2), it returns a
fixed, hardcoded quiz so we can verify the request/response shape and
test the API through /docs before any LLM integration exists.
"""

from fastapi import FastAPI

from models import QuizQuestion, QuizRequest, QuizResponse

app = FastAPI(title="QuizForge API")


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
