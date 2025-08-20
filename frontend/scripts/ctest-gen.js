const ErrorMsg = Object.freeze({
    MISSING_INPUT: "Bitte geben Sie einen Text ein und wählen Sie einen Schwierigkeitsgrad.",
    GENERATION_FAILED: "Fehler bei der Generierung des C-Tests",
    PDF_GENERATION_FAILED: "Fehler beim PDF-Download"
});

const ConsoleLog = Object.freeze({
    UNDFINED: (elem) => `${elem} is undefined`,
    NO_ANSWERS_COLLECT: "Answers could not be collected",
    NO_ELEM_FOUND: (elem) => `${elem} not found`,
    NO_INP_FOR_BLANK: (pos) => `No input found for blank index ${pos}`,
});

const HintMsg = Object.freeze({
    FILENAME: `CTest_${new Date().toISOString().slice(0, 10)}.pdf`,
});

async function generateCTestTextArea() {
    const submitBtn = document.getElementById("generateBtn");
    if (!submitBtn) {
        console.error(ConsoleLog.NO_ELEM_FOUND("generateBtn"));
        return;
    }
    submitBtn.disabled = true;
    try {
        const { input, difficulty } = validateInputs();

        const response = await fetch("/api/create", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ original_text: sanitizeInput(input), difficulty })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData?.message || ErrorMsg.GENERATION_FAILED);
        }

        const data = await response.json();
        setTestAccessData(data);

    } catch (error) {
        console.error(error);
        alert(error.message || ErrorMsg.GENERATION_FAILED);
    } finally {
        submitBtn.disabled = false;
    }
}

function sanitizeInput(text) {
    return text.replace(/<[^>]*>/g, "");
}

function validateInputs() {
    const inputElement = document.getElementById("inputText");
    const difficultyElement = document.querySelector("input[name='difficulty']:checked");

    const input = inputElement?.value.trim();
    const difficulty = difficultyElement?.value;

    if (!input || !difficulty) {
        alert(ErrorMsg.MISSING_INPUT);
        throw new Error(ErrorMsg.MISSING_INPUT);
    }

    return { input, difficulty };
}

function setTestAccessData(data) {
    if (!data || !data.share_url || !data.results_url) {
        throw new Error("Invalid server response: Missing URLs");
    }

    const fullTestLink = window.location.origin + data.share_url;
    const fullResLink = window.location.origin + data.results_url;

    const testLink = document.getElementById("testLink");
    const resLink = document.getElementById("resLink");
    const outputText = document.getElementById("outputText");
    const studCode = document.getElementById("studCode");
    const teachCode = document.getElementById("teachCode");
    const generatedLink = document.getElementById("generatedLink");
    const generatedCodes = document.getElementById("generatedCodes");

    if (testLink) {
        testLink.href = fullTestLink;
        testLink.textContent = fullTestLink;
    }

    if (resLink) {
        resLink.href = fullResLink;
        resLink.textContent = fullResLink;
    }

    if (generatedLink) {
        generatedLink.style.display = "block";
    }

    if (outputText) {
        outputText.textContent = data.ctest_text;
    }

    if (studCode) {
        studCode.textContent = data.student_code;
    }

    if (teachCode) {
        teachCode.textContent = data.teacher_code;
    }

    if (generatedCodes) {
        generatedCodes.style.display = "block";
    }
}

async function downloadPDF() {
    const downloadBtn = document.getElementById("downloadBtn");
    if (!downloadBtn) {
        console.error(ConsoleLog.NO_ELEM_FOUND("downloadBtn"));
        return;
    }

    downloadBtn.disabled = true;

    try {
        const { input, difficulty } = validateInputs();

        const response = await fetch("/api/create_pdf", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ original_text: sanitizeInput(input), difficulty })
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(errorText || ErrorMsg.PDF_GENERATION_FAILED);
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = HintMsg.FILENAME;
        document.body.append(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

    } catch (error) {
        console.error(error);
        alert(error.message || ErrorMsg.PDF_GENERATION_FAILED);
    } finally {
        downloadBtn.disabled = false;
    }
}
