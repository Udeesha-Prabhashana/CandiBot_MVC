from flask import Blueprint, flash, redirect, render_template, session
from utils import insert_score, check_correct

# Create a Blueprint named 'result_controller' for handling result-related routes
bp = Blueprint('result_controller', __name__)

# Route to display the results
@bp.route('/show_results', methods=['GET'])
def show_results():
    # Check if necessary session variables exist
    if 'cv_text' not in session or 'user_answers' not in session:
        flash('Session expired. Please upload the PDF again.')  # Flash an error message
        return redirect('/')  # Redirect to the home page

    # Retrieve session data
    cv_text = session['cv_text']
    user_answers = session['user_answers']
    questions = session['questions']
    user_answers2 = session['user_answers2']
    questions2 = session['questions2']

    correct_count = 0  # Initialize counter for correct answers
    results = []  # List to store question, answer, and correctness

    # Iterate through predefined questions and check answers
    for question in questions:
        answer_data = user_answers.get(question)
        if answer_data:
            answer = answer_data['answer']
            is_generated = answer_data.get('type') == 'generated'
            # Check if the answer is correct
            is_correct = check_correct(question, answer, cv_text, generated=is_generated)
            results.append((question, answer, is_correct))  # Append result tuple to results list
            if is_correct:
                correct_count += 1  # Increment correct answers count if correct

    total_questions = len(questions)  # Total number of predefined questions
    # Calculate score as a percentage
    score = (correct_count / total_questions) * 100

    # Print the score for debugging purposes
    print("Score", score)

    # Insert the score and other data into the database
    insert_score(score, cv_text, user_answers2)

    # Render the results page with the score and results
    return render_template('results.html', score=score, results=results)
