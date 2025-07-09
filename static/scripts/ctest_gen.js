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





