# ✅ utils/analyzer.py (Improved JSON extraction)
import google.generativeai as genai
import re
import json
import os
from dotenv import load_dotenv
from utils.document_parser import extract_qa_pairs

load_dotenv()

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

def analyze_answers(document_text):
    qa_pairs = extract_qa_pairs(document_text)

    if not qa_pairs:
        return [{"error": "No question-answer pairs found in the document"}]

    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    results = []

    for qa_pair in qa_pairs:
        question = qa_pair['question']
        user_answer = qa_pair['answer']
        question_num = qa_pair['question_num']

        prompt = f"""
You are an expert assignment evaluator. Respond strictly in valid JSON format.

Question: {question}
Answer: {user_answer}

Format:
{{
  "is_correct": true,
  "correct_answer": "Expected correct answer",
  "explanation": "Why the answer is right or wrong",
  "suggestion": "How the answer can be improved"
}}
"""

        try:
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            print(f"\n🔍 Gemini Raw Response (Q{question_num}):\n{response_text}\n")

            try:
                analysis = json.loads(response_text)
            except json.JSONDecodeError:
                json_match = re.search(r'\{.*?\}', response_text.replace('\n', ' '), re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group(0))
                else:
                    analysis = {
                        "is_correct": None,
                        "correct_answer": "Unable to determine",
                        "explanation": "Error processing the response",
                        "suggestion": "Please try again"
                    }

            results.append({
                "question_num": question_num,
                "question": question,
                "user_answer": user_answer,
                "is_correct": analysis.get("is_correct", False),
                "correct_answer": analysis.get("correct_answer", ""),
                "explanation": analysis.get("explanation", ""),
                "suggestion": analysis.get("suggestion", "")
            })

        except Exception as e:
            results.append({
                "question_num": question_num,
                "question": question,
                "user_answer": user_answer,
                "error": f"Failed to analyze: {str(e)}"
            })

    return results
