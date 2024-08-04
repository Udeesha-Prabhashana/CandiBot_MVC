import PyPDF2
import requests
import re
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from pymongo import MongoClient, errors
from pymongo.errors import PyMongoError
import certifi
from pymongo.server_api import ServerApi
from model.models import ScoreDocument

load_dotenv()

# Load environment variables
GEMINI_API_ENDPOINT = os.getenv('GEMINI_API_ENDPOINT')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def normalize(text):
    return re.sub(r'\s+|[^a-zA-Z0-9]', '', text).lower()

# Extract text from PDF function
def extract_text_from_pdf(pdf_file):
    pdf_text = ""
    reader = PyPDF2.PdfReader(pdf_file)
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        pdf_text += page.extract_text()
    return pdf_text

# Function to extract the name from the CV text
def extract_name_from_cv(cv_text):
    lines = cv_text.split("\n")
    for line in lines:
        if "name" in line.lower():
            return line.split(":")[1].strip() if ":" in line else line.strip()
    # Fallback to assume the first line is the name if no explicit "name" keyword found
    return lines[0].strip()

# Function to generate questions using the Gemini API
def generate_questions(text):
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [{
            "parts": [{
                "text": f"You are an Interview assistant. Read the following text and generate only 5 questions. Give any explanation about the given questions like this is the this kind of question with the 5 questions don't give anything else for a example (a. You mentioned experience with Python in your skills. Describe a time you used Python to solve a problem in a project. What challenges did you face and how did you overcome them? ) and also b. , c. , d. and e. like this way. and also give the questions according to the user's skills given in the CV. You have to consider all skills to generate the question not only one. For example, if mentioned skills are Python, generate questions related to Python like 'What is Python?', 'What is the use of Python?'. The 2nd question should be a little bit harder than the 1st question, and the 3rd question should be harder than the 1st and 2nd questions like wise. Here is the CV text. You have to give only the questions not any other explanation or anything else and also give the question a. b. c. d. e. like that way:\n\n{text}\n\nQuestions:"
            }]
        }]
    }
    try:
        response = requests.post(f"{GEMINI_API_ENDPOINT}?key={GEMINI_API_KEY}", headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()
        print("Response", response_json)
        if 'candidates' in response_json and response_json['candidates']:
            content = response_json['candidates'][0]['content']['parts'][0]['text']
            questions = extract_questions(content)
            print("Questions", questions)
            return questions
        else:
            return {"Error": "Unable to generate questions. Please try again later."}
    except requests.exceptions.RequestException as e:
        return {"Error": str(e)}

import re

def extract_questions(content):
    # Split the content into lines and filter out the questions
    lines = content.split('\n')
    questions = []
    question_count = 0
    for line in lines:
        # Match lines that start with a letter followed by a period and space
        if re.match(r'^[a-zA-Z]\.\s+', line):
            # Clean up the question text
            question = re.sub(r'^[a-zA-Z]\.\s+', '', line).strip()
            if question:
                questions.append(question)
                question_count += 1
                if question_count == 5:
                    break  # Stop after collecting 5 questions
    return questions

def query_gemini(prompt):
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    try:
        response = requests.post(f"{GEMINI_API_ENDPOINT}?key={GEMINI_API_KEY}", headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()
        print("Response", response_json)

        if 'candidates' in response_json and response_json['candidates']:
            content_parts = response_json['candidates'][0]['content']['parts']
            content = "\n".join(part['text'] for part in content_parts)
            return content.strip()
        else:
            return {"Error": "Unable to generate response content. Please try again later."}

    except requests.exceptions.RequestException as e:
        return {"Error": str(e)}

    except KeyError as e:
        print(f"KeyError: {e}. Response: {response_json}")
        return {"Error": f"KeyError: {e}. Response: {response_json}"}

def validate_answer_llm(question, answer):
    prompt = f"""You are an interview assistant. The following question was asked during an interview, and the candidate provided an answer.

    Question: {question}
    Answer: {answer}

    Is the given answer correct? Answer with only "yes" or "no" and provide a brief explanation.
    """
    try:
        result = query_gemini(prompt)
        print("LLM result:", result)

        if isinstance(result, dict) and "Error" in result:
            print(result["Error"])
            return False

        if "yes" in result.lower():
            return True
        return False

    except Exception as e:
        print(f"Error validating answer with LLM: {e}")
        return False
    
def validate_answer_llm2(question, answer, cv_text):
    prompt = f"""You are an interview assistant. The following question was asked during an interview, and the candidate provided an answer based on their CV.

    CV Text: {cv_text}

    Question: {question}
    Answer: {answer}

    Is the given answer correct according to the CV text? Answer with only "yes" or "no" and provide a brief explanation.
    """
    try:
        result = query_gemini(prompt)  # Assuming query_gemini is the function that calls the LLM
        print("LLM result:", result)

        if isinstance(result, dict) and "Error" in result:
            print(result["Error"])
            return False

        if "yes" in result.lower():
            return True
        return False

    except Exception as e:
        print(f"Error validating answer with LLM: {e}")
        return False

def check_correct(question, answer, text, generated=False):
    if generated:
        return validate_answer_llm(question, answer)
    
    return validate_answer_llm2(question, answer, text)

def calculate_score(user_answers, cv_text):
    correct_count = 0
    total_questions = len(user_answers)
    for question, answer_data in user_answers.items():
        user_answer = answer_data['answer']
        is_generated = answer_data['type'] == 'generated'
        is_correct = check_correct(question, user_answer, cv_text, generated=is_generated)
        print("is_correct ", is_correct)
        if is_correct:
            correct_count += 1
    score = (correct_count / total_questions) * 100
    return round(score, 2)

# Function to extract the name from the CV text using LLM
def get_name_from_llm(cv_text):
    prompt = f"""You are an interview assistant. The task is to extract the name from the given CV text.

    CV Text:
    {cv_text}

    What is the name mentioned in the CV? for a example If the CV mentions "John Doe", the extracted name should be "John Doe".You give the response as only this name without any things
    """
    try:
        response = query_gemini(prompt)
        return response.strip()
    except Exception as e:
        print(f"Error extracting name from LLM: {e}")
        return None

def format_user_answers(user_answers):
    formatted_answers = []
    for question, data in user_answers.items():
        answer = data['answer']
        formatted_answers.append(f"{question} - {answer}")
    return "\n".join(formatted_answers)


# Updated insert_score function using get_name_from_llm
def insert_score(score, cv_text, user_answers2):
    name = get_name_from_llm(cv_text)
    print("Name", name)
    print("Score", score)
    
    HR_QuestionAndAnswers = format_user_answers(user_answers2)
    print("format_user_answers", format_user_answers(user_answers2))

    document = ScoreDocument(name=name, score=score, HR_questions=HR_QuestionAndAnswers)
    ScoreDocument.insert(document)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'
