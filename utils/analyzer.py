import openai
import os
import json
from dotenv import load_dotenv
from utils.document_parser import extract_qa_pairs
from config import OPENAI_API_KEY, OPENAI_MODEL

load_dotenv()
openai.api_key = OPENAI_API_KEY

def analyze_answers(document_text):
    qa_pairs = extract_qa_pairs(document_text)
    
    if not qa_pairs:
        return [{"error": "No question-answer pairs found in the document"}]

    # Create one big prompt for batching
    prompt = "You are an expert assignment evaluator. Analyze the following question-answer pairs and respond with a JSON array:\n\n"
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
        response = openai.Completion.create(
            model=OPENAI_MODEL,
            prompt=prompt,
            temperature=0.3,
            max_tokens=2048
        )

        output_text = response.choices[0].text.strip()

        # Check for empty response or invalid JSON
        if not output_text:
            return [{"error": "No response from OpenAI GPT-4o API"}]

        try:
            json_data = json.loads(output_text)
        except json.JSONDecodeError:
            return [{"error": "Failed to parse GPT response as JSON"}]

        # Merge question and answer back
        for i, analysis in enumerate(json_data):
            analysis["question"] = qa_pairs[i]['question']
            analysis["user_answer"] = qa_pairs[i]['answer']

        return json_data

    except openai.error.OpenAIError as e:
        return [{"error": f"OpenAI API Error: {str(e)}"}]

    except Exception as e:
        return [{"error": f"Unexpected Error: {str(e)}"}]
