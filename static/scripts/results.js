
function renderCTest(text) {
    if (!text || !answersMap) {
        console.error('ctestText or answersMap is undefined');
        return;
    }
    const container = document.getElementById('ctestContainer');
    container.innerHTML = '';
    let blankIndex = 0;
    let i = 0;
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
            input.style.transition = 'none';
            input.style.animation = 'none';
            input.style.pointerEvents = 'none';
            input.readOnly = true;
            input.style.width = `${Math.max(blankLength * 0.8, 2)}em`;
            input.value = studentAnswers[blankIndex];
            container.appendChild(input);
            if (scoreData["detailed_results"][blankIndex]["is_correct"]) {
                input.classList.add('is-correct');
            } else {
                input.classList.add('is-incorrect');
                const correctionSpan = document.createElement('span');
                correctionSpan.classList.add('feedback');
                console.log(scoreData["detailed_results"], blankIndex);
                correctionSpan.innerHTML = ` ❌ <span class="correct-answer">(${scoreData["detailed_results"][blankIndex]["expected_answer"]})</span>`;
                correctionSpan.style.marginLeft = '0.5em';
                input.insertAdjacentElement('afterend', correctionSpan);
            }
            blankIndex++;
            i = nextIndex;
        } else {
            container.appendChild(document.createTextNode(char));
            i++;
        }
    }
}



function initializeCTest() {
    renderCTest(ctestText);
}
document.addEventListener('DOMContentLoaded', initializeCTest);
