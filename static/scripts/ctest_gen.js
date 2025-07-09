async function generateCTest() {
    const selectedDifficulty = document.querySelector('input[name="difficulty"]:checked').value;
    const input = document.getElementById("inputText").value;
    const response = await fetch("/generate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ text: input, difficulty: selectedDifficulty })
    });
    const data = await response.json();
    const fullLink = window.location.origin + data.link;
    const linkContainer = document.getElementById("generatedLink");
    const testLink = document.getElementById("testLink");
    testLink.href = fullLink;
    testLink.textContent = fullLink;
    linkContainer.style.display = "block";
    document.getElementById("outputText").textContent = data.ctest_text;
}
async function downloadPDF() {
    const text = document.getElementById("inputText").value.trim();
    const difficulty = document.querySelector('input[name="difficulty"]:checked')?.value;

    if (!text || !difficulty) {
        alert("Bitte geben Sie den Text und den Schwierigkeitsgrad an.");
        return;
    }

    fetch("/generate_pdf", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            text: text,
            difficulty: difficulty
        })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error("Fehler beim PDF-Download");
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "printable.pdf";
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            console.error(error);
            alert("Fehler beim Generieren des PDFs.");
        });
}







