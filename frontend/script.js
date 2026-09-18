// QuizForge frontend logic.
//
// This handles all three screens: the setup screen (collecting notes +
// question count and generating a quiz), the quiz screen (answering
// questions and scoring them), and the results screen (showing the score
// and per-question feedback). Scoring happens entirely in the browser —
// the quiz questions (including correct answers) are already sitting in
// `currentQuiz` from the /api/quiz response, so no extra API call is
// needed to grade the student's answers.

const API_URL = "http://127.0.0.1:8000/api/quiz";

const setupScreen = document.getElementById("setup-screen");
const quizScreen = document.getElementById("quiz-screen");
const resultsScreen = document.getElementById("results-screen");

const quizForm = document.getElementById("quiz-form");
const notesTextarea = document.getElementById("notes");
const questionCountSelect = document.getElementById("question-count");
const generateButton = document.getElementById("generate-button");
const errorMessage = document.getElementById("error-message");
const loadingMessage = document.getElementById("loading-message");

const answersForm = document.getElementById("answers-form");
const quizQuestionsContainer = document.getElementById("quiz-questions");
const quizErrorMessage = document.getElementById("quiz-error-message");

const scoreHeading = document.getElementById("score-heading");
const resultsList = document.getElementById("results-list");
const restartButton = document.getElementById("restart-button");

// The questions from the most recently generated quiz (as returned by
// the backend). This is the only piece of "state" the app keeps — a
// plain variable holding the array is enough for a project this size.
let currentQuiz = [];

quizForm.addEventListener("submit", handleGenerateQuizSubmit);
answersForm.addEventListener("submit", handleSubmitQuizSubmit);
restartButton.addEventListener("click", handleRestart);

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
    currentQuiz = quiz.questions;
    renderQuiz(currentQuiz);
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
  hideQuizError();
}

function showResultsScreen() {
  quizScreen.hidden = true;
  resultsScreen.hidden = false;
}

function showQuizError(message) {
  quizErrorMessage.textContent = message;
  quizErrorMessage.hidden = false;
}

function hideQuizError() {
  quizErrorMessage.textContent = "";
  quizErrorMessage.hidden = true;
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

// Reads the selected radio button for each question, scores it against
// currentQuiz, and shows the results screen. Blocks submission (with an
// inline message, no alert()) if any question was left unanswered.
function handleSubmitQuizSubmit(event) {
  event.preventDefault();

  const selectedAnswers = currentQuiz.map((question, index) => {
    const checkedInput = document.querySelector(
      `input[name="question-${index}"]:checked`
    );
    return checkedInput ? checkedInput.value : null;
  });

  const hasUnansweredQuestion = selectedAnswers.some(
    (answer) => answer === null
  );
  if (hasUnansweredQuestion) {
    showQuizError("Please answer all questions before submitting.");
    return;
  }
  hideQuizError();

  const results = currentQuiz.map((question, index) => ({
    question: question.question,
    selectedAnswer: selectedAnswers[index],
    correctAnswer: question.correct_answer,
    isCorrect: selectedAnswers[index] === question.correct_answer,
  }));

  const correctCount = results.filter((result) => result.isCorrect).length;

  renderResults(results, correctCount, currentQuiz.length);
  showResultsScreen();
}

// Builds the DOM for the results screen: the score heading, plus one
// block per question showing the student's answer, the correct answer,
// and whether they got it right.
function renderResults(results, correctCount, totalCount) {
  scoreHeading.textContent = `${correctCount} / ${totalCount} correct`;

  resultsList.innerHTML = "";

  results.forEach((result, index) => {
    const resultBlock = document.createElement("div");
    resultBlock.className = `result-block ${
      result.isCorrect ? "correct" : "incorrect"
    }`;

    const questionNumber = document.createElement("p");
    questionNumber.className = "question-number";
    questionNumber.textContent = `Question ${index + 1}`;

    const questionText = document.createElement("p");
    questionText.className = "question-text";
    questionText.textContent = result.question;

    const yourAnswer = document.createElement("p");
    yourAnswer.textContent = `Your answer: ${result.selectedAnswer}`;

    const correctAnswer = document.createElement("p");
    correctAnswer.textContent = `Correct answer: ${result.correctAnswer}`;

    const outcome = document.createElement("p");
    outcome.textContent = result.isCorrect ? "Correct ✓" : "Incorrect ✗";

    resultBlock.appendChild(questionNumber);
    resultBlock.appendChild(questionText);
    resultBlock.appendChild(yourAnswer);
    resultBlock.appendChild(correctAnswer);
    resultBlock.appendChild(outcome);

    resultsList.appendChild(resultBlock);
  });
}

// "Create Another Quiz": clears all quiz/results state and returns to
// the setup screen. The notes textarea is deliberately left alone so the
// student can generate another quiz from the same notes if they want.
function handleRestart() {
  currentQuiz = [];

  quizQuestionsContainer.innerHTML = "";
  resultsList.innerHTML = "";
  scoreHeading.textContent = "";

  hideQuizError();
  hideError();

  resultsScreen.hidden = true;
  quizScreen.hidden = true;
  setupScreen.hidden = false;
}
