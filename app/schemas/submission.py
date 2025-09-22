from pydantic import BaseModel
from typing import Dict



class Submission(BaseModel):
    """
    Model for student test submissions.
    
    Attributes:
        ctest_id (str): 
            UUID of the test being submitted
            
        student_answers (Dict[int, str]):
            Position-to-answer mapping for blanks
            Example: {0: "ick", 1: "ox"}
            
        given_hints (Dict[int, list]):
            Tracks which hints were used for each blank
            Format: {position: [hint symbols]}
    
    Notes:
        - Blank positions are zero-indexed
        - Answer keys must match test's correct_answers structure
    """
    ctest_id: str
    student_answers: Dict[int, str]
    given_hints: Dict[int, list]
    


