import spacy
import spacy.tokens

EASY_BLANKS_PER_SENTENCE_COEFF = 0.1
MEDIUM_BLANKS_PER_SENTENCE_COEFF = 0.4
HARD_BLANKS_PER_SENTENCE_COEFF = 0.7
MINIMAL_WORD_LENGTH = 2
MINIMAL_TEXT_LENGTH = 3
LANGUAGE_PARTS = {"NOUN", "VERB", "ADJ", "ADV"}
BLANK_SYMBOL = "_"



def generate_ctest(text: str, difficulty: str, target_pos=LANGUAGE_PARTS, blanks_per_sentence_coeff=MEDIUM_BLANKS_PER_SENTENCE_COEFF) -> str:
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
                






    


