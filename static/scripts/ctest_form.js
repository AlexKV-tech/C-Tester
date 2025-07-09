function renderCTest(text) {
    if (!text) {
        console.error('ctestText is undefined or null');
        return;
    }

    const container = document.getElementById('ctestContainer');
    container.innerHTML = '';
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
            container.appendChild(input);
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
        .then(async (response) => {
            const data = await response.json();


            if (response.status === 200) {
                showMessage('C-Test erfolgreich abgesendet!', 'success');

                if (data.score) {
                    showMessage(
                        `Ergebnis: ${data.score.correct}/${data.score.total} richtig (${data.score.percentage.toFixed(1)}%)`,
                        'info'
                    );
                }
            } else {
                showMessage('Fehler beim Absenden: ' + (data.message || 'Unbekannter Fehler'), 'danger');
            }
        })
        .catch((error) => {
            console.log(error);
            showMessage('Fehler beim Absenden. Bitte versuchen Sie es erneut.', 'danger');
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