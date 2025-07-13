from pydantic import BaseModel, field_validator
from typing import Dict
from enum import Enum


class DifficultyLevel(str, Enum):
    """
    Enum representing allowed difficulty levels for C-Test generation.
    """
    easy = "easy"
    medium = "medium"
    hard = "hard"


class CTestTextInput(BaseModel):
    """
    Input model for C-Test generation.

    Attributes:
        text (str): The source text to convert into a C-Test.
        difficulty (DifficultyLevel): Difficulty level that influences blank generation.

    Example:
        >>> CTestTextInput(
        ...     text="The quick brown fox jumps over the lazy dog.",
        ...     difficulty=DifficultyLevel.medium
        ... )
    """
    text: str
    difficulty: DifficultyLevel


class CTestSubmission(BaseModel):
    """
    Model for C-Test submissions.

    Attributes:
        test_id (str): Unique identifier of the test.
        answers (Dict[int, str]): Mapping of blank positions to user responses.
        original_text (str): The full reference text for scoring.

    Example:
        >>> CTestSubmission(
        ...     test_id="ct_12345",
        ...     answers={1: "quick", 2: "fox"},
        ...     original_text="The quick brown fox jumps over the lazy dog."
        ... )
    """
    test_id: str
    answers: Dict[int, str]
    original_text: str

    
