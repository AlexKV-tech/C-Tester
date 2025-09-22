from app.models.ctest import CTest
from app.dependencies import get_db
from app.schemas.text_input import TextInput
from app.services.ctest_unit_generator_service import TEST_EXPIRATION_DAYS, create_ctest_unit, generate_code



from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session








"""C-Test generation router for creating and storing language tests."""

ctest_generator_router = APIRouter()


@ctest_generator_router.post("/create")
async def create_test_reply(input: TextInput, db: Session = Depends(get_db)) -> dict[str, str]:
    """
    Endpoint for creating and storing new C-Tests.

    Args:
        input (TextInput): {
            original_text: str,
            difficulty: str
        }
        db (Session): Active database session

    Returns:
        dict: Test creation response containing:
            - ctest_text: The generated test
            - share_url: Student access URL
            - results_url: Teacher results URL
            - student_code: 6-digit access code
            - teacher_code: 6-digit access code

    Raises:
        HTTPException:
            - 400 for invalid input
            - 500 for generation/storage errors

    Workflow:
        1. Validates input text
        2. Generates C-Test content
        3. Creates access codes
        4. Stores test in database
        5. Returns test data with URLs
        6. Sets automatic 7-day expiration
    """
    try:
        ctest_text, correct_answers  = await create_ctest_unit(input.original_text, input.difficulty)
        created_at: datetime = datetime.now(timezone.utc)
        expires_at: datetime = created_at + timedelta(days=TEST_EXPIRATION_DAYS)
        student_code = await generate_code()
        teacher_code = await generate_code()
        ctest_data = {
            "ctest_text": ctest_text,
            "created_at": created_at,
            "expires_at": expires_at,
            "correct_answers": correct_answers,
            "original_text": input.original_text,
            "student_code": student_code,
            "teacher_code": teacher_code
        }

        new_ctest_entry = CTest(**ctest_data)
        db.add(new_ctest_entry)
        db.commit()
        db.refresh(new_ctest_entry)
        return {
            "ctest_text": ctest_text,
            "share_url": f"/api/ctest/{new_ctest_entry.ctest_id}",
            "results_url": f"/api/results/{new_ctest_entry.ctest_id}",
            "student_code": student_code,
            "teacher_code": teacher_code
        }
    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Test generation service error: " + str(e)
        )
