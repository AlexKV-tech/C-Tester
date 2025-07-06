const toggleButton = document.getElementById("themeToggle");
const themeIcon = document.getElementById("themeIcon");

// Apply theme based on system preference or saved choice
function applyTheme(theme) {
    const isLight = theme === "light";

    document.body.classList.toggle("light-mode", isLight);
    themeIcon.classList.toggle("bi-sun-fill", !isLight);
    themeIcon.classList.toggle("bi-moon-fill", isLight);

    toggleButton.classList.toggle("btn-outline-light", !isLight);
    toggleButton.classList.toggle("btn-outline-dark", isLight);
}

// Determine initial theme
const savedTheme = localStorage.getItem("theme");
const prefersLight = window.matchMedia("(prefers-color-scheme: light)").matches;

if (savedTheme) {
    applyTheme(savedTheme);
} else {
    applyTheme(prefersLight ? "light" : "dark");
}

// Theme toggle button click
toggleButton.addEventListener("click", () => {
    const isCurrentlyLight = document.body.classList.contains("light-mode");
    const newTheme = isCurrentlyLight ? "dark" : "light";
    localStorage.setItem("theme", newTheme);
    applyTheme(newTheme);
});
window.matchMedia("(prefers-color-scheme: light)").addEventListener("change", (e) => {
    const savedTheme = localStorage.getItem("theme");
    if (!savedTheme) {
        applyTheme(e.matches ? "light" : "dark");
    }
});
