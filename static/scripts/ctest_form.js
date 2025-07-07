function renderCTest(text) {
    if (!text) {
        console.error('ctestText is undefined or null');
        return;
    }

    const container = document.getElementById('ctestContainer');
    container.innerHTML = '';
    const inputs = [];
    let blankIndex = 0;
    let i = 0;

    while (i < text.length) {
        const char = text[i];
        if (char === '_') {
            const blankLength = blanksMap[blankIndex];
            const nextWordIndex = i + blankLength;
            const input = document.createElement('input');
            input.type = 'text';
            input.name = `blank_${blankIndex}`;
            input.maxLength = blankLength;
            input.className = 'blank-box';
            input.dataset.blankIndex = blankIndex;
            input.style.width = `${Math.max(blankLength * 0.8, 2)}em`;
            /*
            input.addEventListener('input', function () {
                if (input.value.length === input.maxLength) {
                    const currentIndex = inputs.indexOf(input);
                    if (currentIndex < inputs.length - 1) {
                        inputs[currentIndex + 1].focus();
                    }
                }
            });*/
            container.appendChild(input);
            inputs.push(input);
            blankIndex++;
            i = nextWordIndex;
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
        const blankIndex = parseInt(input.dataset.blankIndex);
        userAnswers[blankIndex] = input.value;
    });
    return userAnswers;
}

function showMessage(message, type = 'info') {
    const messageDiv = document.getElementById('responseMessage');
    messageDiv.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
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
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            test_id: testId,
            answers: answers,
            original_text: ctestText
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);

            if (data.status === 'success') {
                showMessage('C-Test erfolgreich abgesendet!', 'success');

                // Show results if available
                if (data.score) {
                    showMessage(
                        `Ergebnis: ${data.score.correct}/${data.score.total} richtig (${data.score.percentage.toFixed(1)}%)`,
                        'info'
                    );
                }

                // Redirect to results page after delay
                setTimeout(() => {
                    window.location.href = `/results/${testId}`;
                }, 2000);
            } else {
                showMessage('Fehler beim Absenden: ' + (data.message || 'Unbekannter Fehler'), 'danger');
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            showMessage('Fehler beim Absenden. Bitte versuchen Sie es erneut.', 'danger');
        })
        .finally(() => {
            // Reset loading state
            submitBtn.textContent = 'Absenden';
            submitBtn.disabled = false;
            form.classList.remove('loading');
        });
}


function initializeCTest() {

    if (typeof ctestText === 'undefined' || typeof blanksMap === 'undefined' || typeof testId === 'undefined') {
        console.error('Required template variables are not defined:', {
            ctestText: typeof ctestText,
            blanksMap: typeof blanksMap,
            testId: typeof testId
        });
        return;
    }

    renderCTest(ctestText);
    document.getElementById('ctestForm').addEventListener('submit', submitAnswers);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeCTest);