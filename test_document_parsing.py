import os
import sys
import logging
from utils.document_parser import extract_text_from_pdf, extract_qa_pairs
from utils.analyzer import analyze_answers
from utils.grader import assign_grade

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("test.log"), logging.StreamHandler()])
logger = logging.getLogger(__name__)

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_document_parsing.py [path_to_pdf]")
        return
    
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return
    
    print(f"Testing file: {pdf_path}")
    
    # Extract text
    print("1. Extracting text...")
    text = extract_text_from_pdf(pdf_path)
    print(f"Extracted {len(text)} characters")
    print("\nSample text:")
    print("=" * 50)
    print(text[:500])
    print("=" * 50)
    
    # Extract QA pairs
    print("\n2. Extracting QA pairs...")
    qa_pairs = extract_qa_pairs(text)
    print(f"Found {len(qa_pairs)} QA pairs")
    
    if qa_pairs:
        print("\nSample QA pairs:")
        for i, qa in enumerate(qa_pairs[:3]):
            print(f"Q{qa['question_num']}: {qa['question']}")
            print(f"A: {qa['answer']}")
            print("-" * 50)
    else:
        print("No QA pairs found!")
    
    # Continue with analysis if QA pairs were found
    if qa_pairs:
        proceed = input("\nContinue with Gemini API analysis? (y/n): ")
        if proceed.lower() == 'y':
            print("\n3. Analyzing answers...")
            analysis_results = analyze_answers(text)
            
            print("\nAnalysis results:")
            for i, result in enumerate(analysis_results[:3]):
                print(f"Q{result['question_num']}: {result['question']}")
                print(f"User answer: {result['user_answer']}")
                print(f"Correct: {result['is_correct']}")
                print(f"Explanation: {result['explanation']}")
                print("-" * 50)
            
            print("\n4. Calculating grade...")
            grade = assign_grade(analysis_results)
            print(f"Grade: {grade['letter']} ({grade['percentage']}%)")
            print(f"Feedback: {grade['feedback']}")

if __name__ == "__main__":
    main()