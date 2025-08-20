function syncClone(text) {
    const clone = document.getElementById("inputClone");
    if (!clone || !text) return;

    clone.style.width = getComputedStyle(text).width;
    clone.style.font = getComputedStyle(text).font;
    clone.style.padding = getComputedStyle(text).padding;
    clone.innerText = text.value + "\u200b";
    text.style.height = clone.scrollHeight + "px";
}

function expandOnInput(text) {
    syncClone(text);
    const btn = document.getElementById("generateBtn");
    if (!btn) return;

    if (text.value.trim().length > 0) {
        btn.classList.remove("btn-outline-primary");
        btn.classList.add("btn-primary");
    } else {
        btn.classList.remove("btn-primary");
        btn.classList.add("btn-outline-primary");
    }
}

function initializeExpand() {
    const text = document.getElementById("inputText");
    if (!text) return;
    syncClone(text);

    text.addEventListener("input", function () {
        expandOnInput(text);
    });

    text.addEventListener("paste", () => {
        requestAnimationFrame(() => {
            syncClone(text);
        });
    });
}

document.addEventListener("DOMContentLoaded", initializeExpand);