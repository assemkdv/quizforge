// QuizForge frontend logic.
//
// This handles the setup screen (collecting notes + question count),
// sends a request to the backend's POST /api/quiz endpoint, and renders
// whatever quiz comes back. Scoring and the results screen are not
// implemented yet (Phase 6) — submitting the quiz form currently does
// nothing.

const API_URL = "http://127.0.0.1:8000/api/quiz";

const setupScreen = document.getElementById("setup-screen");
const quizScreen = document.getElementById("quiz-screen");

const quizForm = document.getElementById("quiz-form");
const notesTextarea = document.getElementById("notes");
const questionCountSelect = document.getElementById("question-count");
const generateButton = document.getElementById("generate-button");
const errorMessage = document.getElementById("error-message");
const loadingMessage = document.getElementById("loading-message");

const answersForm = document.getElementById("answers-form");
const quizQuestionsContainer = document.getElementById("quiz-questions");

quizForm.addEventListener("submit", handleGenerateQuizSubmit);

answersForm.addEventListener("submit", (event) => {
  event.preventDefault();
  // Scoring is added in Phase 6 — for now, Submit Quiz does nothing.
});

async function handleGenerateQuizSubmit(event) {
  event.preventDefault();

  const notes = notesTextarea.value.trim();
  const questionCount = Number(questionCountSelect.value);

  if (notes.length === 0) {
    showError("Please enter some study notes first.");
    return;
  }

  hideError();
  setGeneratingState(true);

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        notes: notes,
        question_count: questionCount,
      }),
    });

    if (!response.ok) {
      throw new Error(`Backend responded with status ${response.status}`);
    }

    const quiz = await response.json();
    renderQuiz(quiz.questions);
    showQuizScreen();
  } catch (error) {
    console.error(error);
    showError("Could not generate the quiz. Please try again.");
  } finally {
    setGeneratingState(false);
  }
}

function setGeneratingState(isGenerating) {
  generateButton.disabled = isGenerating;
  loadingMessage.hidden = !isGenerating;
}

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.hidden = false;
}

function hideError() {
  errorMessage.textContent = "";
  errorMessage.hidden = true;
}

function showQuizScreen() {
  setupScreen.hidden = true;
  quizScreen.hidden = false;
}

// Builds the DOM for every question and drops it into #quiz-questions.
function renderQuiz(questions) {
  quizQuestionsContainer.innerHTML = "";

  questions.forEach((question, index) => {
    const questionElement = createQuestionElement(question, index);
    quizQuestionsContainer.appendChild(questionElement);
  });
}

// Creates the markup for a single question:
//   <div class="question-block">
//     <p class="question-number">Question N</p>
//     <p class="question-text">...</p>
//     <label class="option-label"><input type="radio" ...> Option</label>
//     (repeated for each of the 4 options)
//   </div>
function createQuestionElement(question, index) {
  const questionBlock = document.createElement("div");
  questionBlock.className = "question-block";

  const questionNumber = document.createElement("p");
  questionNumber.className = "question-number";
  questionNumber.textContent = `Question ${index + 1}`;

  const questionText = document.createElement("p");
  questionText.className = "question-text";
  questionText.textContent = question.question;

  questionBlock.appendChild(questionNumber);
  questionBlock.appendChild(questionText);

  // All options for this question share the same "name" attribute, which
  // is what makes the browser treat them as one radio group (selecting
  // one deselects the others in that group). Including the question's
  // index in the name keeps each question's group separate from every
  // other question's group, so selecting an answer in question 2 has no
  // effect on question 1.
  const groupName = `question-${index}`;

  question.options.forEach((option) => {
    const optionLabel = document.createElement("label");
    optionLabel.className = "option-label";

    const optionInput = document.createElement("input");
    optionInput.type = "radio";
    optionInput.name = groupName;
    optionInput.value = option;

    optionLabel.appendChild(optionInput);
    optionLabel.appendChild(document.createTextNode(option));

    questionBlock.appendChild(optionLabel);
  });

  return questionBlock;
}
