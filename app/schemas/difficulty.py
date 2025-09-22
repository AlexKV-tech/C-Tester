from enum import Enum


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
    