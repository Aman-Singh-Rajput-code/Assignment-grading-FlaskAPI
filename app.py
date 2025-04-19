import os
import uuid
import logging
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS

from utils.document_parser import extract_text_from_pdf, extract_text_from_docx
from utils.analyzer import analyze_answers
from utils.grader import assign_grade
from config import OPENAI_API_KEY, UPLOAD_FOLDER, ALLOWED_EXTENSIONS  # Changed to match config.py

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# App configurations
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return jsonify({
        "message": "Smart Assignment Grading API is running 🎯",
        "usage": "POST a .docx or .pdf file to /api/grade-assignment"
    })

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
            # Log the uploaded file details
            logger.debug(f"File uploaded: {filename}, saved to: {file_path}")

            # Extract text from the file based on its extension
            if filename.lower().endswith('.pdf'):
                logger.debug("Extracting text from PDF file.")
                text = extract_text_from_pdf(file_path)
            elif filename.lower().endswith('.docx'):
                logger.debug("Extracting text from DOCX file.")
                text = extract_text_from_docx(file_path)
            else:
                return jsonify({'error': 'Unsupported file type'}), 400

            if not text:
                return jsonify({'error': 'Failed to extract text from the file'}), 400

            # Analyze the extracted answers
            logger.debug("Analyzing answers from extracted text.")
            analysis = analyze_answers(text)

            if not analysis or "error" in analysis[0]:
                return jsonify({'error': 'Failed to analyze answers'}), 400

            # Assign a grade based on the analysis
            grade = assign_grade(analysis)

            # Return the grade and analysis as a JSON response
            return jsonify({
                'grade': grade,
                'analysis': analysis
            })

        except Exception as e:
            # Log the error and return a message to the user
            logger.error(f"Error processing file {filename}: {str(e)}")
            return jsonify({'error': f"An error occurred: {str(e)}"}), 500

    return jsonify({'error': 'File type not allowed'}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0")
