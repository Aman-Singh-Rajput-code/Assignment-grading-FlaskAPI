import google.generativeai as genai
import re
import json
import os
from dotenv import load_dotenv
from utils.document_parser import extract_qa_pairs

load_dotenv()

# Configure Gemini AI
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

def analyze_answers(document_text):
    """
    Analyze the document content to check if answers are correct.
    
    Args:
        document_text (str): The extracted text from the document
        
    Returns:
        list: List of dictionaries containing analysis results
    """
    # Extract question-answer pairs
    qa_pairs = extract_qa_pairs(document_text)

    if not qa_pairs:
        return [{"error": "No question-answer pairs found in the document"}]

    # Initialize Gemini model
    model = genai.GenerativeModel("gemini-1.5-pro-latest")

    results = []

    for qa_pair in qa_pairs:
        question = qa_pair['question']
        user_answer = qa_pair['answer']
        question_num = qa_pair['question_num']
        
        # Create prompt for Gemini
        prompt = f"""
You are an expert assignment evaluator. You must strictly respond in **valid JSON format**.

Evaluate the student's answer and provide feedback.

Question: {question}
Answer: {user_answer}

Format your response like:
{{
  "is_correct": true,
  "correct_answer": "Expected correct answer here",
  "explanation": "Detailed explanation of correctness or error",
  "suggestion": "Improvement suggestion"
}}

Return only JSON. Do not include extra text or commentary.
"""


        try:
            response = model.generate_content(prompt)
            print(f"\n🔍 Gemini Raw Response (Q{question_num}):\n{response.text}\n")

            response_text = response.text

            try:
                analysis = json.loads(response_text)  # Parse response as JSON
            except json.JSONDecodeError:
                # Fallback: Extract JSON using regex
                json_match = re.search(r'({.*})', response_text.replace('\n', ' '), re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group(1))
                else:
                    analysis = {
                        "is_correct": None,
                        "correct_answer": "Unable to determine",
                        "explanation": "Error processing the response",
                        "suggestion": "Please try again"
                    }
            
            # Add original question and answer to the result
            result = {
                "question_num": question_num,
                "question": question,
                "user_answer": user_answer,
                "is_correct": analysis.get("is_correct", False),
                "correct_answer": analysis.get("correct_answer", ""),
                "explanation": analysis.get("explanation", ""),
                "suggestion": analysis.get("suggestion", "")
            }
            
            results.append(result)
        
        except Exception as e:
            results.append({
                "question_num": question_num,
                "question": question,
                "user_answer": user_answer,
                "error": f"Failed to analyze: {str(e)}"
            })

    return results
