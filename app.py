from flask import Flask, request, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
from flask_cors import CORS

from utils.document_parser import extract_text_from_pdf, extract_text_from_docx, extract_qa_pairs
from utils.analyzer import analyze_answers
from utils.grader import assign_grade
from config import API_KEY, UPLOAD_FOLDER, ALLOWED_EXTENSIONS

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/grade-assignment', methods=['POST'])
def grade_assignment():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
        file.save(file_path)

        try:
            if filename.lower().endswith('.pdf'):
                text = extract_text_from_pdf(file_path)
            else:
                text = extract_text_from_docx(file_path)

            qa_pairs = extract_qa_pairs(text)
            analysis = analyze_answers(qa_pairs)
            grade = assign_grade(analysis)

            return jsonify({
                'grade': grade,
                'analysis': analysis
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'File type not allowed'}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port,debug=True)
