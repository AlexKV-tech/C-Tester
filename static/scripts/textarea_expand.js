const text = document.getElementById('inputText');

function syncClone() {
    const clone = document.getElementById('inputClone');
    clone.style.width = getComputedStyle(text).width;
    clone.style.font = getComputedStyle(text).font;
    clone.style.padding = getComputedStyle(text).padding;
    clone.innerText = text.value + '\u200b';
    text.style.height = clone.scrollHeight + 'px';
}

text.addEventListener('input', function () {
    syncClone();
    const btn = document.getElementById('generateBtn');
    if (text.value.trim().length > 0) {
        btn.classList.remove('btn-outline-primary');
        btn.classList.add('btn-primary');
    } else {
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-outline-primary');
    }
});

text.addEventListener('paste', () => requestAnimationFrame(syncClone));
window.addEventListener('load', syncClone);