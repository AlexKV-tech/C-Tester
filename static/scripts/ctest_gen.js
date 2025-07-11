async function generateCTest() {
    const selectedDifficulty = document.querySelector('input[name="difficulty"]:checked')?.value;
    const input = document.getElementById("inputText").value.trim();

    if (!input || !selectedDifficulty) {
        alert("Bitte geben Sie einen Text ein und wählen Sie einen Schwierigkeitsgrad.");
        return;
    }

    try {
        const response = await fetch("/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: input, difficulty: selectedDifficulty })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data?.message || "Fehler bei der Generierung des C-Tests");
        }

        const fullLink = window.location.origin + data.share_url;


        document.getElementById("testLink").href = fullLink;
        document.getElementById("testLink").textContent = fullLink;
        document.getElementById("generatedLink").style.display = "block";
        document.getElementById("outputText").textContent = data.ctest_text;

    } catch (error) {
        console.error(error);
        alert("Fehler beim Generieren des C-Tests. Bitte versuchen Sie es erneut.");
    }
}
async function downloadPDF() {
    const text = document.getElementById("inputText").value.trim();
    const difficulty = document.querySelector('input[name="difficulty"]:checked')?.value;

    if (!text || !difficulty) {
        alert("Bitte geben Sie den Text und den Schwierigkeitsgrad an.");
        return;
    }

    try {
        const response = await fetch("/generate_pdf", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ text, difficulty })
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(errorText || "Fehler beim PDF-Download");
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = "printable.pdf";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

    } catch (error) {
        console.error(error);
        alert("Fehler beim Generieren des PDFs.");
    }
}
