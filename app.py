from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
CORS(app)

# Define absolute path to uploads folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the folder exists

@app.route('/api/grade-assignment', methods=['POST'])
def grade_assignment():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Secure the filename and save it in the absolute uploads folder
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Document extraction logic (dummy for now)
        try:
            qa_pairs = extract_qa_pairs(file_path)
            if not qa_pairs:
                return jsonify({"error": "Failed to extract QA pairs from the document"}), 400
        except Exception as e:
            return jsonify({"error": f"Error in document parsing: {str(e)}"}), 400

        # Answer analysis logic (dummy)
        try:
            analysis_results = analyze_answers(qa_pairs)
            if not analysis_results:
                return jsonify({"error": "Failed to analyze answers"}), 400
        except Exception as e:
            return jsonify({"error": f"Error in answer analysis: {str(e)}"}), 400

        # Return response
        response_data = {
            "grade": {
                "letter": "A",
                "percentage": 95,
                "correct": 9,
                "total": 10,
                "feedback": "Great job!"
            },
            "analysis": analysis_results
        }
        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

def extract_qa_pairs(file_path):
    # Dummy QA extraction logic
    return [
        {"question": "What is the capital of Germany?", "answer": "Berlin"},
        {"question": "Which planet is known as the Red Planet?", "answer": "Mars"}
    ]

def analyze_answers(qa_pairs):
    # Dummy analysis logic
    return [
        {"question_num": 1, "question": "What is the capital of Germany?", "user_answer": "Berlin", "correct": True},
        {"question_num": 2, "question": "Which planet is known as the Red Planet?", "user_answer": "Mars", "correct": True}
    ]

if __name__ == '__main__':
    app.run(debug=True)
