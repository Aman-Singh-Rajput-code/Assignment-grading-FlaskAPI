import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable or use fallback value
API_KEY = os.getenv("GEMINI_API_KEY")

# Check if the API key is properly set
if not API_KEY:
    print("WARNING: Gemini API key not properly configured. Please set the GEMINI_API_KEY environment variable or update the config.py file.")

# File upload settings
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

# Grading thresholds
GRADE_THRESHOLDS = {
    'A': 90,  # 90% or more correct answers
    'B': 80,  # 80-89% correct answers
    'C': 70,  # 70-79% correct answers
    'D': 60,  # 60-69% correct answers
    'F': 0    # Below 60% correct answers
}