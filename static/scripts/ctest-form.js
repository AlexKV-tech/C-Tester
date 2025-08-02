const ERRORS = {
    FORM_SENT: "Dieser Test wurde bereits übermittelt. Änderungen sind nicht mehr möglich.",
};

const SUBMIT_BTN_CONTENT = {
    TRANSFER: "Wird gesendet...",
    SEND: "Absenden",
    SENT: "Bereits gesendet",
};

const CLASS_CORRECT = "is-correct";
const CLASS_INCORRECT = "is-incorrect";

function renderCTestForm(text, correctAnswers) {
    if (!text || !correctAnswers) {
        console.error("ctestText or/and correctAnswers is/are undefined");
        return;
    }

    const container = document.getElementById("ctestContainer");
    if (!container) {
        console.error("Container #ctestContainer not found");
        return;
    }

    const fragment = document.createDocumentFragment();
    container.innerHTML = "";

    let blankIndex = 0;
    let i = 0;

    while (i < text.length) {
        const char = text[i];
        if (char === '_') {
            const answerObj = correctAnswers[blankIndex];
            if (!answerObj || !answerObj.answer) {
                console.warn(`Missing answer for blank index ${blankIndex}`);
                i++;
                continue;
            }

            const blankLength = answerObj.answer.length;
            renderBlankSegment(blankIndex, blankLength, fragment);
            i += blankLength;
            blankIndex++;
        } else {
            renderTextSegment(char, fragment);
            i++;
        }
    }

    container.appendChild(fragment);
}

function renderBlankSegment(blankIndex, blankLength, parent) {
    const input = createLetterInputField(blankIndex, blankLength);
    parent.appendChild(input);
}

function renderTextSegment(char, container) {
    container.appendChild(document.createTextNode(char));
}

function createLetterInputField(blankIndex, blankLength) {
    const input = document.createElement("input");
    input.type = "text";
    input.name = `blank_${blankIndex}`;
    input.maxLength = blankLength;
    input.className = "blank-box";
    input.dataset.blankIndex = blankIndex;
    input.style.width = `${Math.max(blankLength * 0.9, 2)}em`;
    return input;
}

function collectUserInput() {
    const inputs = document.querySelectorAll("#ctestContainer input");
    if (inputs.length === 0) {
        console.error("No blanks found");
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
        console.warn("No responseMessage div found");
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
        console.error("ctestId is undefined");
        return;
    }

    event.preventDefault();

    const studentAnswers = collectUserInput();
    if (!studentAnswers) {
        console.log("Answers could not be collected");
        return;
    }

    const submitBtn = document.getElementById("submitBtn");
    const form = document.getElementById("ctestForm");

    if (!submitBtn || !form) {
        console.error("submitBtn or ctestForm not found");
        return;
    }

    submitBtn.textContent = SUBMIT_BTN_CONTENT.TRANSFER;
    submitBtn.disabled = true;
    form.classList.add("loading");

    try {
        const response = await fetch("/submit-ctest", {
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
        showMessage(error.detail || "Request failed", "danger");
    } finally {
        deactivateSubmitBtn(submitBtn, form);
    }
}

function deactivateSubmitBtn(submitBtn, form) {
    submitBtn.textContent = SUBMIT_BTN_CONTENT.SEND;
    submitBtn.disabled = false;
    form.classList.remove("loading");
}

async function handleResponse(response) {
    const data = await response.json();

    if (response.ok) {
        if (data.was_in_db) {
            showMessage(ERRORS.FORM_SENT, "warning");
            const submitBtn = document.getElementById("submitBtn");
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = SUBMIT_BTN_CONTENT.SENT;
            }
            document.querySelectorAll("#ctestContainer input").forEach(input => {
                input.disabled = true;
            });
            return;
        }

        let finalMessage = data.message || "Ergebnis gespeichert.";
        if (data.score_data) {
            finalMessage += `<br>Ergebnis: ${data.score_data.correct_count}/${data.score_data.total_count} richtig (${data.score_data.percentage.toFixed(2)}%)`;
        }

        showMessage(finalMessage, "success");

        if (data.score_data && data.score_data.detailed_results) {
            const detailedResults = data.score_data.detailed_results;
            Object.keys(detailedResults).forEach(pos => {
                matchLetterAnswerField(pos, detailedResults);
            });
        }
    } else {
        showMessage(`Fehler beim Absenden: ${data.detail || "Unbekannter Fehler"}`, "danger");
    }
}

function matchLetterAnswerField(pos, detailedResults) {
    const entry = detailedResults[pos];
    const input = document.querySelector(`input[name="blank_${pos}"]`);
    if (!input) {
        console.warn(`No input found for blank index ${pos}`);
        return;
    }

    input.disabled = true;

    if (entry.is_correct) {
        input.classList.add(CLASS_CORRECT);
    } else {
        input.classList.add(CLASS_INCORRECT);
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
            if (givenHints.hasOwnProperty(pos)) {
                givenHints[pos] += correctAnswer[firstDiffChar];
            } else {
                givenHints[pos] = correctAnswer[firstDiffChar];
            }
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
            setTimeout(() => { hintCooldown = false; }, 1000);
        });
    }
}

document.addEventListener("DOMContentLoaded", initializeCTestForm);
