import spacy
from fastapi import APIRouter
from schemas import CTestTextInput
from datetime import datetime
from datetime import timedelta
from database import TEST_DB
import uuid

generator_router = APIRouter()

# Constants for C-Test generation
EASY_BLANKS_PER_SENTENCE_COEFF = 0.1
MEDIUM_BLANKS_PER_SENTENCE_COEFF = 0.4
HARD_BLANKS_PER_SENTENCE_COEFF = 0.7
MINIMAL_WORD_LENGTH = 2
MINIMAL_TEXT_LENGTH = 3
LANGUAGE_PARTS = {"NOUN", "VERB", "ADJ", "ADV"}
BLANK_SYMBOL = "_"



def generate_test_unit(text, difficulty, target_pos=LANGUAGE_PARTS, blanks_per_sentence_coeff=MEDIUM_BLANKS_PER_SENTENCE_COEFF):
    """
    Core function that generates CTest based on:
        text -- string representantion of a text to be modified
        difficulty -- string representantion of difficulty of generated C-Test(easy/medium/hard), which determines the coefficient of blanks per sentence
        target_pos -- language parts that are allowed to be modified for C-Test
        blanks_per_sentence_coeff -- coefficient that is determined by dificulty(see constants for easy/medium/hard difficulties)
    Returned values:
        ctest_text -- generated C-Test of type str
        answers -- dictionary in form blanked_index:[{missed part}, {length of missed part}, {start of blanked word}, {start of the blank within a word}, {end of blanked word}]
    """
    if difficulty == "hard":
        blanks_per_sentence_coeff = HARD_BLANKS_PER_SENTENCE_COEFF
    elif difficulty == "easy":
        print(difficulty)
        blanks_per_sentence_coeff = EASY_BLANKS_PER_SENTENCE_COEFF
    nlp = spacy.load("de_core_news_sm")
    doc = nlp(text)
    sentences = list(doc.sents)
    answers = {}
    blanked_word_pos = 0
    ctest_text = list(text)
    
    if len(sentences) < MINIMAL_TEXT_LENGTH:
        return "Der eingegebene Text ist zu kurz"
    for sentence in sentences:
        blanked_sentence_words = 0
        word_count = len([word for word in sentence if word.pos_ in target_pos])
        for word in sentence:
            if word.pos_ in target_pos and word.is_alpha and\
                  len(word) >= MINIMAL_WORD_LENGTH and word_count\
                      and blanked_sentence_words/word_count < blanks_per_sentence_coeff:
                start_word_idx = word.idx
                end_word_idx = word.idx + len(word)
                half_index = (start_word_idx + end_word_idx)//2
                answer = "".join(ctest_text[half_index:end_word_idx])
                ctest_text[half_index:end_word_idx] = list("_" * (end_word_idx - half_index))
                answers[blanked_word_pos] = [answer, len(answer), start_word_idx, half_index, end_word_idx ]
                blanked_word_pos += 1
                blanked_sentence_words += 1
    ctest_text = "".join(ctest_text)
    return ctest_text, answers
                


@generator_router.post("/generate")
async def generate_test_reply(input: CTestTextInput):
    """
    Accept original text(input: CTestTextInput) and generate C-Test from it. 
    Original text, generated C-Test, creation date, expiring data, answers and submission are written into database
    """
    output, answers = generate_test_unit(input.text, input.difficulty)
    test_id = uuid.uuid4().hex[:8]
    created_at = datetime.utcnow()
    time_delta = timedelta(days=7) # time span after which the link for a created test will expire -> all information related to the test_id will be deleted from the DB
    expires_at = created_at + time_delta
    # Write C-Test data into DB - will be replaced by real write operation into database - will be replaced by real DB when deploying
    TEST_DB[test_id] = {
        "ctest_text": output,
        "created_at": created_at,
        "expires_at": expires_at,
        "answers": answers,
        "original_text": input.text,
        "submissions": {}
    }
    return {"ctest_text": output, "link": f"/test/{test_id}", "answers": answers}



    


