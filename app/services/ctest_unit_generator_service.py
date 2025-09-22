import spacy
import random

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


async def create_ctest_unit(original_text: str, difficulty: str) -> tuple[str, dict[int, dict[str, str]]]:
    """
    Generates a C-Test by strategically blanking words in the input text.

    Args:
        original_text (str): The source text to transform into a test
        difficulty (str): Difficulty level ('easy', 'medium', or 'hard')

    Returns:
        tuple: Contains:
            - str: Modified text with blanked words
            - dict: Answer key with structure:
                {
                    blank_index: {
                        "answer": str,  # The blanked text
                        "length": str   # Length of blank in characters
                    }
                }

    Raises:
        ValueError: If:
            - Invalid difficulty level provided
            - Input text is too short (<3 sentences)
            
    Algorithm:
        1. Uses spaCy for German language processing
        2. Targets nouns, verbs, adjectives and adverbs
        3. Blanks are created from word midpoints
        4. Blank frequency scales with difficulty:
            - Easy: ~10% of eligible words
            - Medium: ~40%
            - Hard: ~70%
    """
    if difficulty not in BLANK_COEFF:
        raise ValueError("Invalid difficulty. Must be 'easy', 'medium', or 'hard'.")

    nlp = spacy.load("de_core_news_sm")
    doc = nlp(original_text)
    sentences = list(doc.sents)

    if len(sentences) < MINIMAL_TEXT_LENGTH:
        raise ValueError("Der eingegebene Text ist zu kurz für einen C-Test.")

    blanks_per_sentence_coeff: float = BLANK_COEFF[difficulty]
    ctest_chars: list[str] = list(original_text)
    correct_answers: dict[int, dict[str, str]]  = {}
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

            correct_answers[blank_index] = {"answer": blank_text, "length": str(blank_length)}
            blank_index += 1
            blanks_created += 1

    ctest_output: str = "".join(ctest_chars)
    return ctest_output, correct_answers

async def generate_code():
    """
    Generates a random 6-digit access code.

    Returns:
        str: 6-digit numeric string between 100000-999999

    Note:
        Used for both student and teacher access codes
    """
    return str(random.randint(100000, 999999))