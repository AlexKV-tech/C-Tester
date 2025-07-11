import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
import spacy

from database import TEST_DB
from schemas import CTestTextInput

generator_router = APIRouter()

# Difficulty coefficients
BLANK_COEFF = {
    "easy": 0.1,
    "medium": 0.4,
    "hard": 0.7
}

# Other constants
MINIMAL_WORD_LENGTH = 2
MINIMAL_TEXT_LENGTH = 3
TARGET_POS = {"NOUN", "VERB", "ADJ", "ADV"}
TEST_EXPIRATION_DAYS = 7
BLANK_SYMBOL = "_"


def generate_ctest_unit(text: str, difficulty: str) -> tuple[str, dict]:
    """
    Generates a C-Test from the given text.

    Args:
        text (str): Source text
        difficulty (str): One of "easy", "medium", "hard"

    Returns:
        Tuple:
            - Modified C-Test string
            - Answer metadata dictionary

    Raises:
        ValueError: If invalid difficulty or too short input
    """
    if difficulty not in BLANK_COEFF:
        raise ValueError("Invalid difficulty. Must be 'easy', 'medium', or 'hard'.")

    nlp = spacy.load("de_core_news_sm")
    doc = nlp(text)
    sentences = list(doc.sents)

    if len(sentences) < MINIMAL_TEXT_LENGTH:
        raise ValueError("Der eingegebene Text ist zu kurz für einen C-Test.")

    blanks_per_sentence_coeff = BLANK_COEFF[difficulty]
    ctest_chars = list(text)
    answers = {}
    blank_index = 0

    for sentence in sentences:
        eligible_words = [w for w in sentence if w.pos_ in TARGET_POS and w.is_alpha and len(w.text) >= MINIMAL_WORD_LENGTH]
        max_blanks = max(1, int(len(eligible_words) * blanks_per_sentence_coeff))
        blanks_created = 0

        for word in eligible_words:
            if blanks_created >= max_blanks:
                break

            start = word.idx
            end = start + len(word)
            mid = (start + end) // 2

            blank_length = end - mid
            blank_text = "".join(ctest_chars[mid:end])

            # Replace part of the word with underscores
            ctest_chars[mid:end] = [BLANK_SYMBOL] * blank_length

            answers[blank_index] = [blank_text, blank_length, start, mid, end]
            blank_index += 1
            blanks_created += 1

    ctest_output = "".join(ctest_chars)
    return ctest_output, answers


@generator_router.post("/generate")
async def generate_test_reply(input: CTestTextInput):
    """
    FastAPI endpoint: generates and stores a C-Test from input text.

    Args:
        input: Contains text and difficulty level

    Returns:
        Dictionary with:
            - ctest_text: C-Test with blanks
            - link: Shareable test link
            - answers: Answer key (for dev/debug only)
    """
    try:
        ctest_text, answers = generate_ctest_unit(input.text, input.difficulty)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    test_id = uuid.uuid4().hex[:8]
    created_at = datetime.utcnow()
    expires_at = created_at + timedelta(days=TEST_EXPIRATION_DAYS)

    TEST_DB[test_id] = {
        "ctest_text": ctest_text,
        "created_at": created_at,
        "expires_at": expires_at,
        "answers": answers,
        "original_text": input.text,
        "submissions": {}
    }

    return {
        "test_id": test_id,
        "ctest_text": ctest_text,
        "expires_at": expires_at.isoformat(),
        "share_url": f"/test/{test_id}",
        "answers": answers  # Consider removing in production
    }
