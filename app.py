from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from utils.document_parser import extract_text_from_pdf, extract_text_from_docx, extract_qa_pairs
from utils.analyzer import analyze_answers
from utils.grader import assign_grade
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER

app = Flask(__name__)
CORS(app)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/grade-assignment', methods=['POST'])
def grade_assignment():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Unsupported file type"}), 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        ext = filename.rsplit('.', 1)[1].lower()
        if ext == 'pdf':
            text = extract_text_from_pdf(file_path)
        elif ext in ['doc', 'docx']:
            text = extract_text_from_docx(file_path)
        else:
            return jsonify({"error": "Unsupported file format"}), 400

        if not text.strip():
            return jsonify({"error": "Document is empty or unreadable"}), 400

        analysis_results = analyze_answers(text)

        if "error" in analysis_results[0]:
            return jsonify(analysis_results), 500

        grade_result = assign_grade(analysis_results)

        return jsonify({
            "grade": grade_result,
            "analysis": analysis_results
        })

    except Exception as e:
        print(f"🔥 Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
