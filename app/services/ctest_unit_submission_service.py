async def calculate_score(correct_answers: dict, student_answers: dict):
    """
    Calculate scoring metrics by comparing student answers with correct solutions.

    Args:
        correct_answers (dict): {
            position: {
                "answer": str, 
                "length": str
            }
        }
        student_answers (dict): {position: student_input}

    Returns:
        dict: Score report containing:
            - correct_count (int)
            - total_count (int)
            - percentage (float)
            - detailed_results (dict per position)

    Raises:
        ValueError: If any answer position is missing in correct_answers
    """    
    detailed_results = {}
    correct_count = 0
    
    for position, student_input in student_answers.items():
        expected_answer = ""
        expected_length = "0"
        correct_answer_map = correct_answers.get(str(position))
        if correct_answer_map:
            expected_answer = correct_answer_map.get("answer", "")
            expected_length = correct_answer_map.get("length", "0")
        else:
            raise ValueError(f"Answer on position {position} not found")

        normalized_student_answer = student_input.lower().strip()
        normalized_expected_answer = expected_answer.lower().strip()

        is_correct = normalized_student_answer == normalized_expected_answer
        if is_correct:
            correct_count += 1

        detailed_results[position] = {
            "student_answer": normalized_student_answer,
            "expected_answer": normalized_expected_answer,
            "expected_length": expected_length,
            "is_correct": is_correct
        }

    total_count = len(student_answers)
    percentage = (correct_count / total_count * 100) if total_count > 0 else 0

    return {
        "correct_count": correct_count,
        "total_count": total_count,
        "percentage": percentage,
        "detailed_results": detailed_results
    }


