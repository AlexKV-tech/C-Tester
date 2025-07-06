async function generateCTest() {
    const selectedDifficulty = document.querySelector('input[name="difficulty"]:checked').value;

    const input = document.getElementById("inputText").value;
    console.log(selectedDifficulty);
    const response = await fetch("/generate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ text: input, difficulty: selectedDifficulty })
    });

    const data = await response.json();
    document.getElementById("outputText").textContent = data.ctest;

}





