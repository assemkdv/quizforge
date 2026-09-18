# QuizForge

QuizForge turns pasted study notes into a multiple-choice quiz. Paste your
notes, pick how many questions you want, and the app generates a quiz,
lets you answer it, and shows your score.

It's a small student project built to practice a straightforward
full-stack flow: a Python backend, a call to an LLM API, validating what
the LLM sends back, and a plain HTML/CSS/JS frontend to use it.

## How it works

1. You paste notes and pick a question count on the page and click
   **Generate Quiz**.
2. The frontend sends that to the backend as `POST /api/quiz`.
3. The backend builds a prompt from your notes and sends it to an LLM
   (via the Groq API), asking for multiple-choice questions back as JSON.
4. The backend parses that JSON and validates it with Pydantic — every
   question must have exactly 4 options, and the listed correct answer
   must be one of them. If the LLM's response doesn't hold up, the
   backend returns a clean error instead of passing bad data along.
5. The frontend renders the validated quiz as radio-button questions.
6. When you click **Submit Quiz**, scoring happens entirely in the
   browser (no extra API call) by comparing your selected answers to the
   `correct_answer` already included in the quiz data.
7. You see your score and, per question, what you answered vs. the
   correct answer.

## Tech stack

- **Backend:** Python, FastAPI, Pydantic
- **LLM:** Groq API (`qwen/qwen3.8-27b`)
- **Frontend:** plain HTML, CSS, JavaScript — no framework
- **Tests:** pytest

There's no database, no accounts, and no saved history — each quiz only
exists in the browser tab that generated it.

## Project structure

```
quizforge/
├── backend/
│   ├── main.py              # FastAPI app, the POST /api/quiz route
│   ├── models.py             # Pydantic request/response models + validation
│   ├── quiz_generator.py     # Builds the prompt, calls Groq, validates the result
│   ├── test_models.py        # Tests for the Pydantic validation rules
│   ├── test_quiz_generator.py # Tests for the LLM-facing logic (Groq is mocked)
│   ├── test_main.py          # Tests for the API endpoint (generation is mocked)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html            # Page structure (setup / quiz / results screens)
│   ├── styles.css
│   └── script.js             # Fetch call, quiz rendering, scoring, results
└── README.md
```

## Local setup

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create your own `.env` from the example file, then add a real Groq API
key to it:

```bash
cp .env.example .env
```

Edit `backend/.env` so it looks like:

```
LLM_API_KEY=your-real-groq-api-key
```

**The API key belongs only in `backend/.env`.** That file is listed in
`.gitignore` and must never be committed. `.env.example` is the only one
that's safe to commit — it holds a placeholder, not a real key.

Start the API:

```bash
uvicorn main:app --reload
```

It runs at `http://127.0.0.1:8000`. You can try the endpoint directly at
`http://127.0.0.1:8000/docs`.

### 2. Frontend

In a separate terminal:

```bash
cd frontend
python3 -m http.server 5500
```

Open `http://localhost:5500` in your browser. (Serving it this way,
rather than opening the HTML file directly, gives it a proper origin so
the backend's CORS settings allow it.)

## Example request/response

`POST /api/quiz`

Request body:

```json
{
  "notes": "A relation is reflexive if every element is related to itself. A relation is symmetric if whenever a is related to b, b is also related to a.",
  "question_count": 2
}
```

Response body:

```json
{
  "questions": [
    {
      "question": "Which property requires (a, a) to belong to R?",
      "options": ["Reflexive", "Symmetric", "Transitive", "Antisymmetric"],
      "correct_answer": "Reflexive"
    },
    {
      "question": "Which property requires that if (a, b) is in R, then (b, a) is also in R?",
      "options": ["Reflexive", "Symmetric", "Transitive", "Antisymmetric"],
      "correct_answer": "Symmetric"
    }
  ]
}
```

## Testing

The backend has a small pytest suite covering request/response
validation, the LLM-facing logic in `quiz_generator.py`, and the
`/api/quiz` endpoint. Groq is always mocked in tests — running the suite
never makes a real API call or costs real credits.

```bash
cd backend
source .venv/bin/activate
python3 -m pytest
```
