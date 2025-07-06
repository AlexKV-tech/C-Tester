import spacy
import spacy.tokens

EASY_BLANKS_PER_SENTENCE_COEFF = 0.1
MEDIUM_BLANKS_PER_SENTENCE_COEFF = 0.4
HARD_BLANKS_PER_SENTENCE_COEFF = 0.7
MINIMAL_WORD_LENGTH = 4
MINIMAL_TEXT_LENGTH = 3
TEXT_START_INDEX = 2
LANGUAGE_PARTS = {"NOUN", "VERB", "ADJ", "ADV"}
BLANK_SYMBOL = "_"



def generate_ctest(text: str, difficulty: str, target_pos=LANGUAGE_PARTS, blanks_per_sentence_coeff=MEDIUM_BLANKS_PER_SENTENCE_COEFF) -> str:
    if difficulty == "hard":
        blanks_per_sentence_coeff = HARD_BLANKS_PER_SENTENCE_COEFF
    elif difficulty == "easy":
        blanks_per_sentence_coeff = EASY_BLANKS_PER_SENTENCE_COEFF
    try:
        nlp = spacy.load("de_core_news_sm")
    except Exception as e:
        print(str(e))
    doc = nlp(text)
    sentences = list(doc.sents)
    if len(sentences) < MINIMAL_TEXT_LENGTH:
        return "Der eingegebene Text ist zu kurz"
    ctest_text = []
    for sentence_index, sentence in enumerate(sentences):
        str_sentence = sentences[sentence_index].text
        if sentence_index >= TEXT_START_INDEX:
            blanks_added = 0
            words_count = len([token for token in sentence if token.is_alpha]) 
            for token in sentence:
                str_token = token.text
                word_length = len(str_token)
                is_in_target = (token.is_alpha and token.pos_ in target_pos)
                has_normal_length = (word_length >= MINIMAL_WORD_LENGTH)
                is_enough_blanks =  (words_count and blanks_added/words_count >= blanks_per_sentence_coeff)
                if is_in_target and has_normal_length and not is_enough_blanks:
                    half_index = word_length // 2
                    blanks = " ".join(list(BLANK_SYMBOL * (word_length - half_index)))
                    blanked_word = str_token[:half_index] + blanks
                    str_sentence = str_sentence.replace(str_token, blanked_word)
                    blanks_added += 1
                elif is_enough_blanks:
                    break
                
                        
        ctest_text.append(str_sentence)
    return " ".join(ctest_text)


    


