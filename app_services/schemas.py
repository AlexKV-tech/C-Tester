from pydantic import BaseModel
from typing import Dict
from enum import Enum

"""
Data models for C-Test application.

Defines input/output schemas and enums using Pydantic for:
- Test generation parameters
- Test difficulty levels
- Student submissions
"""


class DifficultyLevel(str, Enum):
    """
    Enumeration of available test difficulty levels.
    
    Levels control blank frequency in generated tests:
    - easy: ~10% of eligible words blanked
    - medium: ~40% of eligible words blanked
    - hard: ~70% of eligible words blanked
    
    Inherits from str for JSON serialization compatibility.
    """
    easy = "easy"
    medium = "medium"
    hard = "hard"
    


class CTestTextInput(BaseModel):
    """
    Request model for C-Test generation endpoint.
    
    Attributes:
        original_text (str): 
            Raw input text (minimum 3 sentences recommended).
            Example: "The quick brown fox jumps over the lazy dog."
            
        difficulty (DifficultyLevel):
            Controls blank frequency and test complexity.
            Default: medium
    
    Validation:
        - Text must be non-empty
        - Minimum length enforced during generation
    """
    original_text: str
    difficulty: DifficultyLevel
    


class CTestSubmission(BaseModel):
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
    


