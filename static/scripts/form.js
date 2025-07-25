
function renderCTest(text) {
    if (!text || !answersMap) {
        console.error('ctestText or answersMap is undefined');
        return;
    }

    const container = document.getElementById('ctestContainer');
    container.innerHTML = '';

    let blankIndex = 0;
    let i = 0;
    console.log(answersMap);

    while (i < text.length) {
        const char = text[i];

        if (char === '_') {
            const blankLength = parseInt(answersMap[blankIndex]);
            if (!blankLength) {
                console.warn(`No length found for blank index ${blankIndex}`);
                break;
            }
            const nextIndex = i + blankLength;
            const input = document.createElement('input');
            input.type = 'text';
            input.name = `blank_${blankIndex}`;
            input.maxLength = blankLength;
            input.className = 'blank-box';
            input.dataset.blankIndex = blankIndex;
            input.style.width = `${Math.max(blankLength * 0.8, 2)}em`;
            container.appendChild(input);
            blankIndex++;
            i = nextIndex;
        } else {
            container.appendChild(document.createTextNode(char));
            i++;
        }
    }
}

function collectUserInput() {
    const inputs = document.querySelectorAll('#ctestContainer input');
    const userAnswers = {};
    inputs.forEach(input => {
        const index = parseInt(input.dataset.blankIndex);
        userAnswers[index] = input.value.trim();
    });
    return userAnswers;
}

function showMessage(message, type = 'info') {
    const messageDiv = document.getElementById('responseMessage');
    messageDiv.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
}

function submitAnswers(event) {
    event.preventDefault();

    const answers = collectUserInput();
    const submitBtn = document.getElementById('submitBtn');
    const form = document.getElementById('ctestForm');

    submitBtn.textContent = 'Wird gesendet...';
    submitBtn.disabled = true;
    form.classList.add('loading');

    fetch('/submit-ctest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            test_id: testId,
            answers: answers,
            original_text: ctestText
        })
    })
        .then(async (response) => {
            const data = await response.json();

            if (response.ok) {
                if (data.present) {
                    showMessage("Dieser Test wurde bereits übermittelt. Änderungen sind nicht mehr möglich.", 'warning');


                    const submitBtn = document.getElementById('submitBtn');
                    submitBtn.disabled = true;
                    submitBtn.textContent = 'Bereits gesendet';


                    document.querySelectorAll('#ctestContainer input').forEach(input => {
                        input.disabled = true;
                    });
                    return;
                }
                showMessage(data.message, 'success');
                if (data.score) {
                    showMessage(
                        `Ergebnis: ${data.score.correct}/${data.score.total} richtig (${data.score.percentage}%)`,
                        'info'
                    );
                }
                const detailedResults = data.score.detailed_results;

                // Loop through each blank and apply feedback
                Object.keys(detailedResults).forEach(pos => {
                    const entry = detailedResults[pos];

                    // Query the corresponding input by name
                    const input = document.querySelector(`input[name="blank_${pos}"]`);

                    if (!input) {
                        console.warn(`No input found for blank index ${pos}`);
                        return;
                    }

                    // Disable the input after submission
                    input.disabled = true;

                    // Add CSS classes for visual feedback
                    if (entry.is_correct) {
                        input.classList.add('is-correct');
                    } else {
                        input.classList.add('is-incorrect');

                        // Create a span with the correct answer
                        const correctionSpan = document.createElement('span');
                        correctionSpan.classList.add('feedback');
                        correctionSpan.innerHTML = ` ❌ <span class="correct-answer">(${entry.expected_answer})</span>`;
                        correctionSpan.style.marginLeft = '0.5em';

                        // Insert after the input
                        input.insertAdjacentElement('afterend', correctionSpan);
                    }
                });




            } else {
                showMessage(`Fehler beim Absenden: ${data.detail || 'Unbekannter Fehler'
                    }`, 'danger');
            }
        })
        .catch(error => {
            console.error(error);
            showMessage(data.detail, 'danger');
        })
        .finally(() => {
            submitBtn.textContent = 'Absenden';
            submitBtn.disabled = false;
            form.classList.remove('loading');
        });
}

function initializeCTest() {
    renderCTest(ctestText);
    document.getElementById('ctestForm').addEventListener('submit', submitAnswers);
}

document.addEventListener('DOMContentLoaded', initializeCTest);
