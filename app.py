from flask import Flask, request, jsonify
from flask_cors import CORS 
import os

app = Flask(__name__)
CORS(app)

@app.route('/api/grade-assignment', methods=['POST'])
def grade_assignment():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Save the file
        file_path = f"./uploads/{file.filename}"
        file.save(file_path)
        
        # Document extraction logic (assuming DOCX file for this example)
        try:
            # Dummy logic for extracting questions and answers
            # Replace this with actual document parsing
            qa_pairs = extract_qa_pairs(file_path)
            if not qa_pairs:
                return jsonify({"error": "Failed to extract QA pairs from the document"}), 400
        except Exception as e:
            return jsonify({"error": f"Error in document parsing: {str(e)}"}), 400
        
        # Analyze answers (dummy logic for now)
        try:
            analysis_results = analyze_answers(qa_pairs)
            if not analysis_results:
                return jsonify({"error": "Failed to analyze answers"}), 400
        except Exception as e:
            return jsonify({"error": f"Error in answer analysis: {str(e)}"}), 400
        
        # Prepare and return the response
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
    # Replace with actual logic to extract QA pairs from the uploaded document
    # Dummy implementation
    return [
        {"question": "What is the capital of Germany?", "answer": "Berlin"},
        {"question": "Which planet is known as the Red Planet?", "answer": "Mars"}
    ]

def analyze_answers(qa_pairs):
    # Replace with actual analysis logic
    # Dummy implementation
    return [{"question_num": 1, "user_answer": "Berlin", "correct": True}]

if __name__ == '__main__':
    app.run(debug=True)
