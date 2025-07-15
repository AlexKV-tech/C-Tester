from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import spacy
from database import get_db
from schemas import CTestTextInput
import models

generator_router = APIRouter()
BLANK_COEFF = {
    "easy": 0.1,
    "medium": 0.4,
    "hard": 0.7
}
MINIMAL_WORD_LENGTH = 2
MINIMAL_TEXT_LENGTH = 3
TARGET_POS = {"NOUN", "VERB", "ADJ", "ADV"}
TEST_EXPIRATION_DAYS = 7
BLANK_SYMBOL = "_"


def generate_ctest_unit(text: str, difficulty: str) -> tuple[str, dict[int, dict[str, str]]]:
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

    blanks_per_sentence_coeff: float = BLANK_COEFF[difficulty]
    ctest_chars: list[str] = list(text)
    answers: dict[int, dict[str, str]]  = {}
    blank_index: int = 0

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

            
            ctest_chars[mid:end] = [BLANK_SYMBOL] * blank_length

            answers[blank_index] = {"answer": blank_text, "length": str(blank_length)}
            blank_index += 1
            blanks_created += 1

    ctest_output: str = "".join(ctest_chars)
    return ctest_output, answers


@generator_router.post("/generate")
async def generate_test_reply(input: CTestTextInput, db: Session = Depends(get_db)) -> dict[str, str]:
    """
    FastAPI endpoint: generates and stores a C-Test from input text.

    Args:
        input: Contains text and difficulty level

    Returns:
        Dictionary with:
            - ctest_text: C-Test with blanks
            - link: Shareable test link
            - answers: Answer key (for debug only)
    """
    try:
        ctest_text, answers  = generate_ctest_unit(input.text, input.difficulty)
        created_at: datetime = datetime.now(timezone.utc)
        expires_at: datetime = created_at + timedelta(days=TEST_EXPIRATION_DAYS)
        ctest_data = {
            "ctest_text": ctest_text,
            "created_at": created_at,
            "expires_at": expires_at,
            "answers": answers,
            "original_text": input.text,
        }

        new_ctest_entry = models.CTest(**ctest_data)
        db.add(new_ctest_entry)
        db.commit()
        db.refresh(new_ctest_entry)
        return {
            "ctest_text": ctest_text,
            "share_url": f"/test/{new_ctest_entry.test_id}",
        }
    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Test generation service error: " + str(e)
        )
