from flask import Blueprint, flash, redirect, request, session, url_for, render_template, jsonify
from utils import extract_text_from_pdf, allowed_file, generate_questions

# Create a Blueprint named 'file_controller' for organizing routes related to file handling
bp = Blueprint('file_controller', __name__)

# Define some predefined questions to use in the application
predefined_questions = [
    "What is your full name?",
    "What university did you attend?",
    "What is your current GPA?"
]

# Route for the index page
@bp.route('/')
def index():
    return render_template('index.html')  # Render the 'index.html' template

# Route for handling file uploads
@bp.route('/upload', methods=['POST'])
def upload_file():
    # Check if a file is included in the request
    if 'file' not in request.files:
        flash('No file part')  # Show an error message if no file is found
        return redirect(request.url)  # Redirect back to the upload page

    # Get the file from the request
    file = request.files['file']

    # Check if the file has no name
    if file.filename == '':
        flash('No selected file')  # Show an error message if no file is selected
        return redirect(request.url)  # Redirect back to the upload page

    # Check if the file is valid and allowed
    if file and allowed_file(file.filename):
        # Extract text from the uploaded PDF file
        pdf_text = extract_text_from_pdf(file)
        if pdf_text:
            # Generate interview questions based on the extracted text
            generated_questions = generate_questions(pdf_text)

            # Check if there was an error generating questions
            if isinstance(generated_questions, dict) and "Error" in generated_questions:
                flash('Error: Unable to generate questions. Please try again later.')
                return redirect(request.url)  # Redirect back to the upload page

            # Save relevant information in the session
            session['cv_text'] = pdf_text
            session['questions'] = predefined_questions + generated_questions
            session['current_question_index'] = 0
            session['user_answers'] = {}

            # Redirect to the chat page
            return redirect(url_for('file_controller.chat'))
        else:
            flash('Error: Unable to extract text from PDF')  # Show an error message if text extraction fails
            return redirect(request.url)  # Redirect back to the upload page
    else:
        flash('Invalid file type. Please upload a PDF.')  # Show an error message for invalid file types
        return redirect(request.url)  # Redirect back to the upload page

# Route for the chat page
@bp.route('/chat', methods=['GET'])
def chat():
    return render_template('chat.html')  # Render the 'chat.html' template
