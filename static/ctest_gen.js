async function generateCTest() {
    const input = document.getElementById("inputText").value;

    const response = await fetch("/generate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ text: input })
    });

    const data = await response.json();
    document.getElementById("outputText").textContent = data.ctest;

}





