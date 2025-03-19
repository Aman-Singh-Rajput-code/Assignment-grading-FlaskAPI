from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
import uuid
import traceback
import logging
from werkzeug.utils import secure_filename
import google.generativeai as genai
from utils.document_parser import extract_text_from_pdf, extract_text_from_docx, extract_qa_pairs
from utils.analyzer import analyze_answers
from utils.grader import assign_grade
from config import API_KEY, UPLOAD_FOLDER, ALLOWED_EXTENSIONS

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()])
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.secret_key = os.urandom(24)

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure Gemini API
try:
    genai.configure(api_key=API_KEY)
    logger.info("Gemini API configured successfully")
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {str(e)}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        logger.info("File upload initiated")
        if 'file' not in request.files:
            logger.warning("No file part in request")
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            logger.warning("No selected file")
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            # Generate unique filename
            filename = str(uuid.uuid4()) + "_" + secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            logger.info(f"File saved to {filepath}")
            
            # Process file based on extension
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            
            if file_ext == 'pdf':
                logger.info("Processing PDF file")
                text_content = extract_text_from_pdf(filepath)
            elif file_ext in ['doc', 'docx']:
                logger.info("Processing DOCX file")
                text_content = extract_text_from_docx(filepath)
            else:
                logger.error(f"Unsupported file format: {file_ext}")
                return jsonify({'error': 'Unsupported file format'}), 400
            
            logger.info(f"Extracted text content (first 100 chars): {text_content[:100] if text_content else 'No text extracted'}")
            
            # Extract QA pairs
            qa_pairs = extract_qa_pairs(text_content)
            logger.info(f"Extracted {len(qa_pairs)} QA pairs")
            
            # If no QA pairs found, return error
            if not qa_pairs:
                logger.error("No question-answer pairs found in the document")
                os.remove(filepath)
                return jsonify({'error': 'No question-answer pairs found in the document'}), 400
            
            # Analyze the document content
            logger.info("Starting answer analysis")
            analysis_results = analyze_answers(text_content)
            
            # Calculate overall grade
            logger.info("Calculating overall grade")
            overall_grade = assign_grade(analysis_results)
            
            # Store results in session
            session['analysis_results'] = analysis_results
            session['overall_grade'] = overall_grade
            
            # Clean up the uploaded file
            os.remove(filepath)
            logger.info(f"Uploaded file removed: {filepath}")
            
            return redirect(url_for('show_results'))
        else:
            logger.warning(f"Invalid file format: {file.filename}")
            return jsonify({'error': 'Invalid file format'}), 400
            
    except Exception as e:
        logger.error(f"Error in upload_file: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/results')
def show_results():
    try:
        analysis_results = session.get('analysis_results', None)
        overall_grade = session.get('overall_grade', None)
        
        logger.info(f"Retrieved from session - analysis_results: {type(analysis_results)} with {len(analysis_results) if analysis_results else 0} items")
        logger.info(f"Retrieved from session - overall_grade: {overall_grade}")
        
        if not analysis_results:
            logger.warning("No analysis results found in session")
            return redirect(url_for('index'))
        
        return render_template('results.html', 
                              results=analysis_results,
                              overall_grade=overall_grade)
    except Exception as e:
        logger.error(f"Error in show_results: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500
    
@app.route('/debug/upload', methods=['POST'])
def debug_upload():
    """Debug endpoint for troubleshooting document parsing."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            # Generate unique filename
            filename = str(uuid.uuid4()) + "_" + secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process file based on extension
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            
            if file_ext == 'pdf':
                text_content = extract_text_from_pdf(filepath)
            elif file_ext in ['doc', 'docx']:
                text_content = extract_text_from_docx(filepath)
            else:
                return jsonify({'error': 'Unsupported file format'}), 400
            
            # Extract QA pairs
            qa_pairs = extract_qa_pairs(text_content)
            
            # Clean up the uploaded file
            os.remove(filepath)
            
            # Return debug info
            return jsonify({
                'text_content_length': len(text_content),
                'text_content_sample': text_content[:1000],
                'qa_pairs_count': len(qa_pairs),
                'qa_pairs': qa_pairs[:5]  # Return first 5 QA pairs
            })
        
        return jsonify({'error': 'Invalid file format'}), 400
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/debug')
def debug_page():
    """Debug page for uploading files."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Debug Document Parsing</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            form { margin-bottom: 20px; }
            #result { white-space: pre-wrap; background: #f0f0f0; padding: 10px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>Debug Document Parsing</h1>
        <form id="upload-form" enctype="multipart/form-data">
            <input type="file" name="file" accept=".pdf,.doc,.docx" required>
            <button type="submit">Upload and Debug</button>
        </form>
        <div id="result"></div>
        
        <script>
            document.getElementById('upload-form').addEventListener('submit', function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const resultDiv = document.getElementById('result');
                
                resultDiv.textContent = 'Uploading and analyzing...';
                
                fetch('/debug/upload', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    resultDiv.textContent = JSON.stringify(data, null, 2);
                })
                .catch(error => {
                    resultDiv.textContent = 'Error: ' + error;
                });
            });
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
