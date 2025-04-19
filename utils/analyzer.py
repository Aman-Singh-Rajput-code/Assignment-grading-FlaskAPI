import openai
import os
import json
import traceback
from dotenv import load_dotenv
from utils.document_parser import extract_qa_pairs
from config import OPENAI_API_KEY, OPENAI_MODEL
from openai import OpenAIError  # Correct import

load_dotenv()
openai.api_key = OPENAI_API_KEY

def analyze_answers(document_text):
    qa_pairs = extract_qa_pairs(document_text)

    if not qa_pairs:
        return [{"error": "No question-answer pairs found in the document"}]

    # Build the prompt
    prompt = "Analyze the following question-answer pairs and return the results in JSON format:\n\n"
    prompt += "[\n"
    for pair in qa_pairs:
        prompt += f'''  {{
    "question_num": "{pair['question_num']}",
    "question": "{pair['question']}",
    "user_answer": "{pair['answer']}"
  }},\n'''
    prompt = prompt.rstrip(",\n") + "\n]\n"

    prompt += """
Now, return a JSON array of objects using this format:
[
  {
    "question_num": "1",
    "is_correct": true,
    "correct_answer": "Expected correct answer",
    "explanation": "Why the answer is right or wrong",
    "suggestion": "How the answer can be improved"
  },
  ...
]
"""

    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert assignment evaluator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2048
        )

        output_text = response['choices'][0]['message']['content'].strip()
        print("\n🧪 GPT-4o Raw Output:\n", output_text)

        json_data = json.loads(output_text)

        for i, analysis in enumerate(json_data):
            analysis["question"] = qa_pairs[i]['question']
            analysis["user_answer"] = qa_pairs[i]['answer']

        return json_data

    except OpenAIError as e:
        print("🔥 OpenAI API Error:", e)
        traceback.print_exc()
        return [{"error": f"OpenAI API Error: {str(e)}"}]

    except Exception as e:
        print("🔥 Unexpected error:", e)
        traceback.print_exc()
        return [{"error": f"Unexpected error: {str(e)}"}]
