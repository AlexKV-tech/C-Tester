function applyTheme(theme, themeIcon, toggleButton) {
    const isLight = theme === "light";
    document.body.classList.toggle("light-mode", isLight);

    if (themeIcon) {
        themeIcon.classList.toggle("bi-sun-fill", !isLight);
        themeIcon.classList.toggle("bi-moon-fill", isLight);
    }

    if (toggleButton) {
        toggleButton.classList.toggle("btn-outline-light", !isLight);
        toggleButton.classList.toggle("btn-outline-dark", isLight);
    }
}

function themeSwitch() {
    const toggleButton = document.getElementById("themeToggle");
    const themeIcon = document.getElementById("themeIcon");
    if (!toggleButton || !themeIcon) return;

    const savedTheme = localStorage.getItem("theme");
    const prefersLight = window.matchMedia("(prefers-color-scheme: light)").matches;

    applyTheme(savedTheme || (prefersLight ? "light" : "dark"), themeIcon, toggleButton);

    toggleButton.addEventListener("click", () => {
        const isCurrentlyLight = document.body.classList.contains("light-mode");
        const newTheme = isCurrentlyLight ? "dark" : "light";
        localStorage.setItem("theme", newTheme);
        applyTheme(newTheme, themeIcon, toggleButton);
    });

    window.matchMedia("(prefers-color-scheme: light)").addEventListener("change", (e) => {
        if (!localStorage.getItem("theme")) {
            applyTheme(e.matches ? "light" : "dark", themeIcon, toggleButton);
        }
    });
}

if (document.readyState !== "loading") {
    themeSwitch();
} else {
    document.addEventListener("DOMContentLoaded", themeSwitch);
} 