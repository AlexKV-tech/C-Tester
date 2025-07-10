from pydantic import BaseModel
from typing import Dict

class CTestTextInput(BaseModel):
    text: str # text to be modified
    difficulty: str # difficulty of ther test either easy, medium or hard

class CTestSubmission(BaseModel):
    test_id: str 
    answers: Dict[int, str]  # answers of a user in form <index of answer>: <answer>
    original_text: str # original text that was blanked 
