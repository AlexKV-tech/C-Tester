from app.schemas.difficulty import DifficultyLevel

from pydantic import BaseModel


class TextInput(BaseModel):
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
    