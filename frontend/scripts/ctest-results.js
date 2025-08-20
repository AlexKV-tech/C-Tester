const State = Object.freeze({
    CORRECT: "is-correct",
    INCORRECT: "is-incorrect",
});
const ConsoleLog = Object.freeze({
    NO_ELEM_FOUND: (elem) => `${elem} not found`,
    NO_VALID_ANSWER_FOR_BLANK: (blankIndex) => `No valid answer length for blank ${blankIndex}`,
    MISSING_REQ_PARAMS: "Missing required parameters",
    NO_SCORE_DETAILS_FOR_BLANK: (blankIndex) => `No score details for blank ${blankIndex}`,
});
const HintMsg = Object.freeze({
    GIVEN_HINT: (givenHint) => `(Gegebener Hinweis: ${givenHint})`
});

const MIN_INPUT_WIDTH_EM = 2;
const WIDTH_SCALE_FACTOR = 0.8;

function renderCTestResults(text, correctAnswers, studentAnswers, scoreData, givenHints) {
    if (!text || !correctAnswers || !studentAnswers || !scoreData) {
        console.error(ConsoleLog.MISSING_REQ_PARAMS);
        return;
    }

    const container = document.getElementById("ctestContainer");
    if (!container) {
        console.error(ConsoleLog.NO_ELEM_FOUND("#ctestContainer"));
        return;
    }

    container.innerHTML = "";
    const fragment = document.createDocumentFragment();

    let blankIndex = 0;
    let i = 0;

    while (i < text.length) {
        let word = "";
        while (i < text.length && text[i] !== " ") {
            word += text[i];
            i++;
        }

        const wordSpan = document.createElement("span");
        wordSpan.className = "word";

        let j = 0;
        while (j < word.length) {
            if (word[j] === "_") {
                const answer = correctAnswers[blankIndex]?.answer;
                const blankLength = answer?.length;

                if (!blankLength) {
                    console.warn(ConsoleLog.NO_INP_FOR_BLANK(blankIndex));
                    j++;
                    continue;
                }
                renderBlankSegment(blankIndex, blankLength, wordSpan, studentAnswers, scoreData, givenHints);
                j += blankLength;
                blankIndex++;
            } else {
                renderTextSegment(word[j], wordSpan);
                j++;
            }
        }
        fragment.append(wordSpan);
        if (i < text.length && text[i] === " ") {
            fragment.append(" ");
            i++;
        }
    }

    container.append(fragment);
}


function addGivenHint(blankIndex, givenHints, container) {
    const givenHint = givenHints[blankIndex];
    if (givenHint) {
        container.append(document.createTextNode(HintMsg.GIVEN_HINT(givenHint)));
    }
}
function renderBlankSegment(blankIndex, blankLength, container, studentAnswers, scoreData, givenHints) {
    const input = createLetterAnswerField(blankIndex, blankLength);
    input.value = studentAnswers[blankIndex] || "";
    container.append(input);
    addGivenHint(blankIndex, givenHints, container);
    applyScoreFeedback(input, blankIndex, scoreData);
}

function applyScoreFeedback(input, blankIndex, scoreData) {
    const details = scoreData.detailed_results?.[blankIndex];
    if (!details) {
        console.warn(ConsoleLog.NO_SCORE_DETAILS_FOR_BLANK(blankIndex));
        return;
    }

    if (details.is_correct) {
        input.classList.add(State.CORRECT);
    } else {
        input.classList.add(State.INCORRECT);
        const correctionSpan = document.createElement("span");
        correctionSpan.className = "feedback";
        correctionSpan.innerHTML = ` ❌ <span class="correct-answer">(${details.expected_answer})</span>`;
        correctionSpan.style.marginLeft = "0.5em";
        input.insertAdjacentElement("afterend", correctionSpan);
    }
}

function renderTextSegment(char, container) {
    container.append(document.createTextNode(char));
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
