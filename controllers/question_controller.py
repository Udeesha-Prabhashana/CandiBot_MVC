from flask import Blueprint, jsonify, request, session, redirect, url_for

# Create a Blueprint named 'question_controller' for handling question-related routes
bp = Blueprint('question_controller', __name__)

# Define a list of predefined questions
predefined_questions = [
    "What is your full name?",
    "What university did you attend?",
    "What is your current GPA?"
]

# Define a list of HR-related questions
hr_questions = [
    "What is your expected salary in LKR?",
    "When is the possible join date for you?",
    "Do you prefer WFH, WFO or hybrid?",
    "What are your preferred working hours?"
]

# Route to get the next question from the session
@bp.route('/get_question', methods=['GET'])
def get_question():
    # Check if the necessary session variables exist
    if 'questions' not in session or 'current_question_index' not in session:
        return jsonify({'error': 'Session expired. Please upload the PDF again.'}), 400

    current_index = session['current_question_index']
    questions = session['questions']

    # Check if there are more questions to return
    if current_index < len(questions):
        current_question = questions[current_index]
        return jsonify({'question': current_question})
    else:
        return jsonify({'error': 'No more questions.'}), 400
    

# Route to get the next HR question from the session
@bp.route('/get_hr_question', methods=['GET'])
def get_question2():
    # Check if the necessary session variables exist
    if 'questions2' not in session or 'current_question_index' not in session:
        return jsonify({'error': 'Session expired. Please upload the PDF again.'}), 400

    current_index = session['current_question_index']
    questions2 = session['questions2']

    # Check if there are more HR questions to return
    if current_index < len(questions2):
        current_question = questions2[current_index]
        return jsonify({'question': current_question})
    else:
        return jsonify({'error': 'No more questions.'}), 400

# Route to submit an answer for a question
@bp.route('/submit_answer', methods=['POST'])
def submit_answer():
    # Check if the necessary session variables exist
    if 'questions' not in session or 'current_question_index' not in session:
        return jsonify({'error': 'Session expired. Please upload the PDF again.'}), 400

    current_index = session['current_question_index']
    questions = session['questions']

    # Check if there are more questions to answer
    if current_index >= len(questions):
        return jsonify({'error': 'No more questions.'}), 400

    # Get the answer from the form data
    answer = request.form.get('answer')
    if not answer:
        return jsonify({'error': 'Answer cannot be empty.'}), 400  # Ensure the answer is not empty

    # Determine if the question is predefined or generated
    question_type = 'generated' if current_index >= len(predefined_questions) else 'predefined'
    # Store the answer in the session
    session['user_answers'][questions[current_index]] = {'answer': answer, 'type': question_type}
    session['current_question_index'] += 1

    # Debug prints for tracking state
    print("length", len(session['questions']))
    print("session['current_question_index']", session['current_question_index'])

    # Check if all questions have been answered
    if session['current_question_index'] >= len(session['questions']):
        # Redirect to HR questions route after completing all questions
        return redirect(url_for('question_controller.ask_hr_questions'))

    return jsonify({'success': 'Answer submitted successfully.'})

# Route to initialize HR questions and redirect to the chat page
@bp.route('/ask_hr_questions')
def ask_hr_questions():
    # Reset session variables for HR questions
    session['current_question_index'] = 0  # Start from the first HR question
    session['questions2'] = hr_questions  # Set HR questions for session
    session['user_answers2'] = {}  # Initialize an empty dictionary to store HR answers
    return redirect(url_for('file_controller.chat'))  # Redirect to the chat page

# Route to submit an answer for an HR question
@bp.route('/submit_hr_answers', methods=['POST'])
def submit_hr_answers():
    # Check if the necessary session variables exist
    if 'questions2' not in session or 'current_question_index' not in session:
        return jsonify({'error': 'Session expired. Please upload the PDF again.'}), 400

    current_index = session['current_question_index']
    questions = session['questions2']

    # Check if there are more HR questions to answer
    if current_index >= len(questions):
        return jsonify({'error': 'No more questions.'}), 400

    # Get the answer from the form data
    answer = request.form.get('answer')
    if not answer:
        return jsonify({'error': 'Answer cannot be empty.'}), 400  # Ensure the answer is not empty

    # Store the answer in the session
    session['user_answers2'][questions[current_index]] = {'answer': answer}
    session['current_question_index'] += 1

    # Debug prints for tracking state
    print("length of HR questions", len(session['questions2']))
    print("session['current_question_index'] - HR", session['current_question_index'])

    # Check if all HR questions have been answered
    if session['current_question_index'] >= len(session['questions2']):
        # Prepare to redirect to show results
        cv_text = session['cv_text']
        hr_answers = session['user_answers2']

        # Return a response indicating completion
        return jsonify({'completed': True})

    return jsonify({'success': 'Answer submitted successfully.'})
