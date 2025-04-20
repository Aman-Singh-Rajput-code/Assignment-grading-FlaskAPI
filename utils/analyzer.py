import openai
import os
import json
import re
from dotenv import load_dotenv
from utils.document_parser import extract_qa_pairs

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4o")

def analyze_answers(document_text):
    qa_pairs = extract_qa_pairs(document_text)

    if not qa_pairs:
        return [{"error": "No question-answer pairs found in the document"}]

    results = []

    for qa in qa_pairs:
        question = qa['question']
        answer = qa['answer']
        question_num = qa['question_num']

        prompt = f"""
You are an expert assignment evaluator. Respond strictly in valid JSON format.

Question: {question}
Answer: {answer}

Format:
{{
  "is_correct": true,
  "correct_answer": "Expected correct answer",
  "explanation": "Why the answer is right or wrong",
  "suggestion": "How the answer can be improved"
}}
"""

        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )

            response_text = response.choices[0].message.content.strip()

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
                        "explanation": "Error processing response",
                        "suggestion": "Please try again"
                    }

            results.append({
                "question_num": question_num,
                "question": question,
                "user_answer": answer,
                "is_correct": analysis.get("is_correct", False),
                "correct_answer": analysis.get("correct_answer", ""),
                "explanation": analysis.get("explanation", ""),
                "suggestion": analysis.get("suggestion", "")
            })

        except Exception as e:
            results.append({
                "question_num": question_num,
                "question": question,
                "user_answer": answer,
                "error": f"OpenAI error: {str(e)}"
            })

    return results
