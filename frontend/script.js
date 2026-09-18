// QuizForge frontend logic.
//
// Phase 1 note: this file only wires up the setup screen (notes input,
// question count, and basic validation). There is no backend yet, so
// clicking "Generate Quiz" does not send any request. The actual
// POST /api/quiz call will be added once the backend exists (Phase 3).

const quizForm = document.getElementById("quiz-form");
const notesTextarea = document.getElementById("notes");
const questionCountSelect = document.getElementById("question-count");
const generateButton = document.getElementById("generate-button");
const errorMessage = document.getElementById("error-message");
const loadingMessage = document.getElementById("loading-message");

quizForm.addEventListener("submit", handleGenerateQuizSubmit);

function handleGenerateQuizSubmit(event) {
  event.preventDefault();

  const notes = notesTextarea.value.trim();
  const questionCount = Number(questionCountSelect.value);

  if (notes.length === 0) {
    showError("Please enter some study notes first.");
    return;
  }

  hideError();

  // Placeholder for now — Phase 3 will replace this with a real call to
  // POST /api/quiz and use the response to render the quiz screen.
  console.log("Ready to generate quiz with:", { notes, questionCount });
}

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.hidden = false;
}

function hideError() {
  errorMessage.textContent = "";
  errorMessage.hidden = true;
}
