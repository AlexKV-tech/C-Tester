
import spacy

BLANKS_PER_SENTENCE_COEFF = 0.4
MINIMAL_WORD_LENGTH = 4
MINIMAL_TEXT_LENGTH = 3
TEXT_START_INDEX = 2
LANGUAGE_PARTS = {"NOUN", "VERB", "ADJ", "ADV"}
BLANK_SYMBOL = "_"

def generate_ctest(text: str, target_pos=LANGUAGE_PARTS, blanks_per_sentence_coeff=BLANKS_PER_SENTENCE_COEFF):
    nlp = spacy.load("de_core_news_sm")
    doc = nlp(text)
    sentences = list(doc.sents)
    if len(sentences) < MINIMAL_TEXT_LENGTH:
        raise ValueError("Text too short")
    ctest_text = []
    for sentence_index, sentence in enumerate(sentences):
        str_sentence = sentences[sentence_index].text
        if (sentence_index >= TEXT_START_INDEX):
            blanks_added = 0
            words_count = len([token for token in sentence if token.is_alpha]) 
            for token in sentence:
                str_token = token.text
                word_length = len(str_token)
                if token.pos_ in target_pos and token.is_alpha and word_length >= MINIMAL_WORD_LENGTH and blanks_added/words_count < blanks_per_sentence_coeff:
                    half_index = word_length // 2
                    blanks = " ".join(list(BLANK_SYMBOL * (word_length - half_index)))
                    blanked_word = str_token[:half_index] + blanks
                    str_sentence = str_sentence.replace(str_token, blanked_word)
                    blanks_added += 1
                        
        ctest_text.append(str_sentence)
    return " ".join(ctest_text)


    


