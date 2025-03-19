from config import GRADE_THRESHOLDS

def assign_grade(analysis_results):
    """
    Assign an overall grade based on the analysis results.
    
    Args:
        analysis_results (list): The analysis results for each question-answer pair
        
    Returns:
        dict: Grade information including letter grade, percentage, and feedback
    """
    if not analysis_results or "error" in analysis_results[0]:
        return {
            "letter": "N/A",
            "percentage": 0,
            "feedback": "Unable to grade due to document parsing issues."
        }
    
    # Count correct answers
    total_questions = len(analysis_results)
    correct_answers = sum(1 for result in analysis_results if result.get("is_correct", False))
    
    # Calculate percentage
    if total_questions > 0:
        percentage = (correct_answers / total_questions) * 100
    else:
        percentage = 0
    
    # Determine letter grade
    letter_grade = "F"
    for grade, threshold in sorted(GRADE_THRESHOLDS.items(), key=lambda x: x[1], reverse=True):
        if percentage >= threshold:
            letter_grade = grade
            break
    
    # Generate feedback based on performance
    if percentage >= 90:
        feedback = "Excellent work! You've demonstrated a thorough understanding of the material."
    elif percentage >= 80:
        feedback = "Good job! You have a solid grasp of most concepts, with some room for improvement."
    elif percentage >= 70:
        feedback = "Satisfactory work. You understand the basics but should review some key concepts."
    elif percentage >= 60:
        feedback = "You need improvement. Please review the material and focus on the areas where you made mistakes."
    else:
        feedback = "Significant improvement needed. Please review all the material carefully and consider seeking additional help."
    
    return {
        "letter": letter_grade,
        "percentage": round(percentage, 1),
        "feedback": feedback,
        "correct": correct_answers,
        "total": total_questions
    }