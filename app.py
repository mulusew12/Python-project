# app.py
import streamlit as st
import json
import time
from datetime import datetime
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="🎯 Python Quiz Master",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Load questions
@st.cache_data
def load_questions():
    try:
        with open('questions.json', 'r') as f:
            data = json.load(f)
            return data['questions']
    except FileNotFoundError:
        st.error("questions.json file not found!")
        return []

# Initialize session state for quiz variables
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = []
if 'time_remaining' not in st.session_state:
    st.session_state.time_remaining = 15
if 'timer_running' not in st.session_state:
    st.session_state.timer_running = False

# Load questions
questions = load_questions()

# Welcome screen
if st.session_state.current_question == 0 and not st.session_state.user_answers:
    st.title("🎯 Python Quiz Master")
    st.markdown("""
    Welcome to the Ultimate Python Quiz!
    
    • Multiple choice and True/False questions
    • 15 seconds per question
    • Instant feedback
    • Detailed results at the end
    
    Test your Python knowledge and see how you score!
    """)
    if st.button("Start Quiz"):
        st.session_state.current_question = 1
        st.session_state.score = 0
        st.session_state.user_answers = []
        st.rerun()

# Quiz logic
if st.session_state.current_question > 0 and st.session_state.current_question <= len(questions):
    question_data = questions[st.session_state.current_question - 1]
    
    # Display progress
    st.progress(st.session_state.current_question / len(questions))
    st.header(f"Question {st.session_state.current_question}/{len(questions)}")
    st.subheader(question_data['question'])
    
    # Timer display
    if st.session_state.timer_running:
        st.write(f"Time remaining: {st.session_state.time_remaining}s")
    
    # Options
    options = question_data['options']
    user_answer = st.radio("Select your answer:", options, key=f"q{st.session_state.current_question}")
    
    # Submit button
    if st.button("Submit Answer"):
        st.session_state.timer_running = False
        correct_answer = question_data['correct_answer']
        is_correct = user_answer == correct_answer
        
        if is_correct:
            st.session_state.score += 1
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Incorrect! The correct answer is: {correct_answer}")
        
        # Store answer
        st.session_state.user_answers.append({
            "question": question_data['question'],
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "correct": is_correct
        })
        
        # Move to next question or results
        if st.session_state.current_question < len(questions):
            st.session_state.current_question += 1
            st.session_state.time_remaining = 15
            st.session_state.timer_running = False
        else:
            st.session_state.current_question = -1  # Signal end of quiz
        st.rerun()

# Results screen
if st.session_state.current_question == -1:
    st.title("Quiz Results")
    score_percentage = (st.session_state.score / len(questions)) * 100
    
    if score_percentage >= 80:
        emoji = "🎉"
        message = "Excellent! You're a Python expert!"
    elif score_percentage >= 60:
        emoji = "👍"
        message = "Good job! You know your Python!"
    else:
        emoji = "📚"
        message = "Keep learning! You'll get better!"
    
    st.subheader(f"{emoji} Final Score: {st.session_state.score}/{len(questions)} ({score_percentage:.1f}%)")
    st.write(message)
    
    # Review answers
    for i, answer in enumerate(st.session_state.user_answers):
        with st.expander(f"Question {i+1}: {answer['question']}"):
            if answer['correct']:
                st.write(f"Your answer: ✅ {answer['user_answer']}")
            else:
                st.write(f"Your answer: ❌ {answer['user_answer']}")
                st.write(f"Correct answer: {answer['correct_answer']}")
    
    # Save results
    if st.button("Save Results"):
        result_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "score": st.session_state.score,
            "total_questions": len(questions),
            "percentage": score_percentage
        }
        try:
            existing_df = pd.read_csv('results.csv')
            results_df = pd.concat([existing_df, pd.DataFrame([result_data])], ignore_index=True)
        except FileNotFoundError:
            results_df = pd.DataFrame([result_data])
        results_df.to_csv('results.csv', index=False)
        st.success("Results saved successfully! 📊")
    
    if st.button("Try Again"):
        st.session_state.current_question = 0
        st.session_state.score = 0
        st.session_state.user_answers = []
        st.rerun()