const ErrorMsg = Object.freeze({
    FORM_SENT: "Dieser Test wurde bereits übermittelt. Änderungen sind nicht mehr möglich.",
    UNKNOWN: "Unbekannter Fehler",
    SEND_ERROR: (detail) => `Fehler beim Absenden: ${detail || UNKNOWN}`,
    REQ_FAILED: "Die Anfrage ist fehlgeschlagen",

});
const HintMsg = Object.freeze({
    TRANSFER: "Wird gesendet...",
    SEND: "Absenden",
    SENT: "Bereits gesendet",
    RESULT: (correct_count,
        total_count,
        percentage) =>
        `Ergebnis: ${correct_count}/${total_count} richtig (${percentage}%)`,
    SAVED: "Ergebnis gespeichert."
});

const State = Object.freeze({
    CORRECT: "is-correct",
    INCORRECT: "is-incorrect",
});
const ConsoleLog = Object.freeze({
    UNDFINED: (elem) => `${elem} is undefined`,
    NO_ANSWERS_COLLECT: "Answers could not be collected",
    NO_ELEM_FOUND: (elem) => `${elem} not found`,
    NO_INP_FOR_BLANK: (pos) => `No input found for blank index ${pos}`,
});


function renderCTestForm(text, correctAnswers) {
    const container = document.getElementById("ctestContainer");
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
                const answerObj = correctAnswers[blankIndex];
                const blankLength = answerObj.answer.length;
                wordSpan.append(createLetterInputField(blankIndex, blankLength));
                j += blankLength;
                blankIndex++;
            } else {
                wordSpan.append(document.createTextNode(word[j]));
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
function renderBlankSegment(blankIndex, blankLength, parent) {
    parent.append(createLetterInputField(blankIndex, blankLength));
}

function renderTextSegment(char, container) {
    container.append(document.createTextNode(char));
}

function createLetterInputField(blankIndex, blankLength) {
    const input = document.createElement("input");
    input.type = "text";
    input.name = `blank_${blankIndex}`;
    input.maxLength = blankLength;
    input.className = "blank-box";
    input.dataset.blankIndex = blankIndex;
    input.style.width = `${blankLength * 0.8}em`;
    return input;
}

function collectUserInput() {
    const inputs = document.querySelectorAll("#ctestContainer input");
    if (inputs.length === 0) {
        console.error(ConsoleLog.NO_ELEM_FOUND("input blank"));
        return null;
    }
    const userAnswers = {};
    inputs.forEach(input => {
        const index = parseInt(input.dataset.blankIndex);
        userAnswers[index] = input.value.trim();
    });

    return userAnswers;
}

function showMessage(message, type = "info") {
    const messageDiv = document.getElementById("responseMessage");
    if (!messageDiv) {
        console.warn(ConsoleLog.NO_ELEM_FOUND("responseMessage"));
        return;
    }
    messageDiv.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
}

async function submitCTest(event, ctestId, givenHints) {
    if (!ctestId) {
        console.error(ConsoleLog.UNDFINED("cTestID"));
        return;
    }

    event.preventDefault();

    const studentAnswers = collectUserInput();
    if (!studentAnswers) {
        console.log(ConsoleLog.NO_ANSWERS_COLLECT);
        return;
    }

    const submitBtn = document.getElementById("submitBtn");
    const form = document.getElementById("ctestForm");

    if (!submitBtn || !form) {
        console.error(ConsoleLog.NO_ELEM_FOUND("submitBtn or form"));
        return;
    }

    submitBtn.textContent = HintMsg.TRANSFER;
    submitBtn.disabled = true;
    form.classList.add("loading");

    try {
        const response = await fetch("/api/submit-ctest", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                ctest_id: ctestId,
                student_answers: studentAnswers,
                given_hints: givenHints
            })
        });

        await handleResponse(response);
    } catch (error) {
        console.error(error);
        showMessage(error.detail || ErrorMsg.REQ_FAILED, "danger");
    } finally {
        deactivateSubmitBtn(submitBtn, form);
    }
}

function deactivateSubmitBtn(submitBtn, form) {
    submitBtn.textContent = HintMsg.SEND;
    submitBtn.disabled = false;
    form.classList.remove("loading");
}

async function handleResponse(response) {
    const data = await response.json();
    if (response.ok) {
        if (data.was_in_db) {
            showMessage(ErrorMsg.FORM_SENT, "warning");
            const submitBtn = document.getElementById("submitBtn");
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = HintMsg.SENT;
            }
            document.querySelectorAll("#ctestContainer input").forEach(input => {
                input.disabled = true;
            });
            return;
        }
        let finalMessage = data.message || HintMsg.SAVED;
        if (data.score_data) {
            console.log(data.percentage);
            finalMessage += "<br>" + HintMsg.RESULT(data.score_data.correct_count,
                data.score_data.total_count,
                data.score_data.percentage.toFixed(2).toString());
        }
        showMessage(finalMessage, "success");
        if (data.score_data && data.score_data.detailed_results) {
            const detailedResults = data.score_data.detailed_results;
            Object.keys(detailedResults).forEach(pos => {
                matchLetterAnswerField(pos, detailedResults);
            });
        }
    } else {
        showMessage(ErrorMsg.SEND_ERROR(data.detail), "danger");
    }
}

function matchLetterAnswerField(pos, detailedResults) {
    const entry = detailedResults[pos];
    const input = document.querySelector(`input[name="blank_${pos}"]`);
    if (!input) {
        console.warn(ConsoleLog.NO_INP_FOR_BLANK(pos));
        return;
    }
    input.disabled = true;
    if (entry.is_correct) {
        input.classList.add(State.CORRECT);
    } else {
        input.classList.add(State.INCORRECT);
        const correctionSpan = document.createElement("span");
        correctionSpan.classList.add("feedback");
        correctionSpan.innerHTML = ` ❌ <span class="correct-answer">(${entry.expected_answer})</span>`;
        correctionSpan.style.marginLeft = "0.5em";
        input.insertAdjacentElement("afterend", correctionSpan);
    }
}

function getHint(correctAnswers, givenHints) {
    const blanksCount = Object.keys(correctAnswers).length;

    for (let pos = 0; pos < blanksCount; pos++) {
        const input = document.querySelector(`input[name="blank_${pos}"]`);
        if (!input) continue;

        const givenAnswer = input.value.trim();
        const correctAnswer = (correctAnswers[pos]?.answer || "").trim();

        if (givenAnswer !== correctAnswer) {
            let firstDiffChar = 0;
            while (givenAnswer[firstDiffChar] === correctAnswer[firstDiffChar]) {
                firstDiffChar++;
            }

            input.value = input.value.slice(0, firstDiffChar) + correctAnswer[firstDiffChar];
            if (!givenHints.hasOwnProperty(pos)) {
                givenHints[pos] = new Array(correctAnswer.length);
            }
            givenHints[pos][firstDiffChar] = correctAnswer[firstDiffChar];
            break;
        }
    }
}

function initializeCTestForm() {
    const correctAnswers = _correctAnswers;
    const ctestId = _ctestId;
    const ctestText = _ctestText;
    let givenHints = {};

    renderCTestForm(ctestText, correctAnswers);

    const form = document.getElementById("ctestForm");
    if (form) {
        form.addEventListener("submit", (event) => {
            submitCTest(event, ctestId, givenHints);
        });
    }

    let hintCooldown = false;
    const hintBtn = document.getElementById("hintBtn");
    if (hintBtn) {
        hintBtn.addEventListener("click", () => {
            if (hintCooldown) return;
            getHint(correctAnswers, givenHints);
            hintCooldown = true;
            setTimeout(() => { hintCooldown = false; }, 10);
        });
    }
}

document.addEventListener("DOMContentLoaded", initializeCTestForm);
