import openai
import json
import re
import os
from dotenv import load_dotenv
from utils.document_parser import extract_qa_pairs
from config import API_KEY, OPENAI_MODEL

load_dotenv()
openai.api_key = API_KEY

def analyze_answers(document_text):
    qa_pairs = extract_qa_pairs(document_text)

    if not qa_pairs:
        return [{"error": "No question-answer pairs found in the document"}]

    results = []

    for qa in qa_pairs:
        question = qa['question']
        user_answer = qa['answer']
        question_num = qa['question_num']

        prompt = f"""
You are an expert assignment evaluator. Strictly respond with JSON only.

Question: {question}
Answer: {user_answer}

Return this format:
{{
  "is_correct": true,
  "correct_answer": "Expected correct answer",
  "explanation": "Why the answer is right or wrong",
  "suggestion": "How to improve the answer"
}}
"""

        try:
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

            response_text = response['choices'][0]['message']['content'].strip()
            print(f"\n📩 GPT Response (Q{question_num}):\n{response_text}\n")

            try:
                analysis = json.loads(response_text)
            except json.JSONDecodeError:
                match = re.search(r'\{.*?\}', response_text, re.DOTALL)
                if match:
                    analysis = json.loads(match.group(0))
                else:
                    analysis = {
                        "is_correct": None,
                        "correct_answer": "Unable to determine",
                        "explanation": "Invalid JSON format in response.",
                        "suggestion": "Try again with a valid answer."
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
                "error": f"OpenAI error: {str(e)}"
            })

    return results
