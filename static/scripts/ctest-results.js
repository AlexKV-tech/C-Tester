const CLASS_CORRECT = "is-correct";
const CLASS_INCORRECT = "is-incorrect";
const MIN_INPUT_WIDTH_EM = 2;
const WIDTH_SCALE_FACTOR = 0.8;

function renderCTestResults(text, correctAnswers, studentAnswers, scoreData, givenHints) {
    if (!text || !correctAnswers || !studentAnswers || !scoreData) {
        console.error("Missing required parameters");
        return;
    }

    const container = document.getElementById("ctestContainer");
    if (!container) {
        console.error("Container #ctestContainer not found");
        return;
    }

    container.innerHTML = "";
    const fragment = document.createDocumentFragment();

    let blankIndex = 0;
    let i = 0;

    while (i < text.length) {
        const char = text[i];
        if (char === "_") {
            const answer = correctAnswers[blankIndex]?.answer;
            const blankLength = answer?.length;

            if (!blankLength) {
                console.warn(`No valid answer length for blank ${blankIndex}`);
                i++;
                continue;
            }

            renderBlankSegment(blankIndex, blankLength, fragment, studentAnswers, scoreData, givenHints);
            i += blankLength;
            blankIndex++;
        } else {
            renderTextSegment(char, fragment);
            i++;
        }
    }

    container.appendChild(fragment);
}
function addGivenHint(blankIndex, givenHints, container) {
    const givenHint = givenHints[blankIndex];
    if (givenHint) {
        container.appendChild(document.createTextNode(`(Gegebener Hinweis: ${givenHint})`));
    }
}
function renderBlankSegment(blankIndex, blankLength, container, studentAnswers, scoreData, givenHints) {
    const input = createLetterAnswerField(blankIndex, blankLength);
    input.value = studentAnswers[blankIndex] || "";
    container.appendChild(input);
    addGivenHint(blankIndex, givenHints, container);
    applyScoreFeedback(input, blankIndex, scoreData);
}

function applyScoreFeedback(input, blankIndex, scoreData) {
    const details = scoreData.detailed_results?.[blankIndex];
    if (!details) {
        console.warn(`No score details for blank ${blankIndex}`);
        return;
    }

    if (details.is_correct) {
        input.classList.add(CLASS_CORRECT);
    } else {
        input.classList.add(CLASS_INCORRECT);
        const correctionSpan = document.createElement("span");
        correctionSpan.className = "feedback";
        correctionSpan.innerHTML = ` ❌ <span class="correct-answer">(${details.expected_answer})</span>`;
        correctionSpan.style.marginLeft = "0.5em";
        input.insertAdjacentElement("afterend", correctionSpan);
    }
}

function renderTextSegment(char, container) {
    container.appendChild(document.createTextNode(char));
}

function createLetterAnswerField(blankIndex, blankLength) {
    const input = document.createElement("input");
    input.type = "text";
    input.name = `blank_${blankIndex}`;
    input.maxLength = blankLength;
    input.className = "blank-box";
    input.dataset.blankIndex = blankIndex;
    input.readOnly = true;
    input.style.transition = "none";
    input.style.animation = "none";
    input.style.pointerEvents = "none";
    input.style.width = `${Math.max(blankLength * WIDTH_SCALE_FACTOR, MIN_INPUT_WIDTH_EM)}em`;
    return input;
}

function initializeCTestResults() {
    const correctAnswers = _correctAnswers;
    const ctestText = _ctestText;
    const studentAnswers = _studentAnswers;
    const scoreData = _scoreData;
    const givenHints = _givenHints;
    renderCTestResults(ctestText, correctAnswers, studentAnswers, scoreData, givenHints);
}

document.addEventListener("DOMContentLoaded", initializeCTestResults);
