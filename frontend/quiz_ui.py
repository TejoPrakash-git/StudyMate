import streamlit as st
import json
from api_layer.mcq_generator import MCQGenerator

def render_quiz():
    """Render the quiz generator UI component."""
    st.header("Quiz Generator")
    st.write("Generate quizzes based on your study materials.")
    
    # Initialize session state variables if they don't exist
    if "quiz_questions" not in st.session_state:
        st.session_state.quiz_questions = []
    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}
    if "quiz_results" not in st.session_state:
        st.session_state.quiz_results = None
    if "mcq_generator" not in st.session_state:
        st.session_state.mcq_generator = MCQGenerator()
    
    # Quiz generation options
    st.subheader("Generate a Quiz")
    
    # Quiz source selection
    quiz_source = st.radio(
        "Quiz Source",
        ["From PDF", "From Text Input", "From Topics"]
    )
    
    col1, col2 = st.columns(2)
    with col1:
        num_questions = st.number_input("Number of Questions", min_value=1, max_value=20, value=5)
    with col2:
        difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"], index=1)
    
    # Source-specific inputs
    if quiz_source == "From PDF":
        if "pdf_text" in st.session_state and st.session_state.pdf_text:
            st.success("Using the currently loaded PDF.")
            content_source = st.session_state.pdf_text
        else:
            st.warning("No PDF loaded. Please upload a PDF in the PDF Study Assistant section first.")
            content_source = None
        
        # Optional topic focus
        topics = st.text_input("Focus on specific topics (comma-separated, optional):")
        topic_list = [t.strip() for t in topics.split(",")] if topics else None
    
    elif quiz_source == "From Text Input":
        content_source = st.text_area("Enter the study material text:", height=200)
        topic_list = None
    
    elif quiz_source == "From Topics":
        topics = st.text_input("Enter topics (comma-separated):")
        topic_list = [t.strip() for t in topics.split(",")] if topics else []
        content_source = "Generate questions about the following topics: " + ", ".join(topic_list) if topic_list else ""
    
    # Generate quiz button
    if st.button("Generate Quiz", key="generate_quiz_button"):
        if content_source:
            with st.spinner("Generating quiz questions..."):
                try:
                    # Generate MCQs
                    if quiz_source == "From PDF" and topic_list:
                        questions = st.session_state.mcq_generator.generate_quiz_from_pdf(
                            content_source, num_questions, topic_list, difficulty
                        )
                    else:
                        questions = st.session_state.mcq_generator.generate_mcqs(
                            content_source, num_questions, difficulty
                        )
                    
                    # Store in session state
                    st.session_state.quiz_questions = questions
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_results = None
                    
                    st.success(f"Generated {len(questions)} questions!")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error generating quiz: {str(e)}")
        else:
            st.error("Please provide content for the quiz.")
    
    # Display quiz if questions are available
    if st.session_state.quiz_questions:
        st.subheader("Quiz")
        
        # Quiz form
        with st.form(key="quiz_form"):
            for i, question in enumerate(st.session_state.quiz_questions):
                st.markdown(f"**Question {i+1}:** {question['question']}")
                
                # Display options
                selected_option = st.radio(
                    f"Select an answer for question {i+1}:",
                    [opt.split('. ', 1)[1] if '. ' in opt else opt for opt in question['options']],
                    key=f"q{i}"
                )
                
                # Store the selected answer (just the letter)
                option_index = [opt.split('. ', 1)[1] if '. ' in opt else opt for opt in question['options']].index(selected_option)
                st.session_state.quiz_answers[i] = question['options'][option_index].split('. ')[0]
                
                st.markdown("---")
            
            # Submit button
            submit_button = st.form_submit_button("Submit Answers")
            
            if submit_button:
                # Calculate results
                correct_count = 0
                results = []
                
                for i, question in enumerate(st.session_state.quiz_questions):
                    user_answer = st.session_state.quiz_answers.get(i, "")
                    correct_answer = question['correct_answer']
                    is_correct = user_answer == correct_answer
                    
                    if is_correct:
                        correct_count += 1
                    
                    results.append({
                        "question": question['question'],
                        "user_answer": user_answer,
                        "correct_answer": correct_answer,
                        "is_correct": is_correct,
                        "explanation": question.get('explanation', "")
                    })
                
                # Store results
                st.session_state.quiz_results = {
                    "score": correct_count,
                    "total": len(st.session_state.quiz_questions),
                    "percentage": round(correct_count / len(st.session_state.quiz_questions) * 100, 1),
                    "details": results
                }
        
        # Display results if available
        if st.session_state.quiz_results:
            st.subheader("Quiz Results")
            results = st.session_state.quiz_results
            
            # Score
            st.markdown(f"**Score:** {results['score']} / {results['total']} ({results['percentage']}%)")
            
            # Progress bar
            st.progress(results['score'] / results['total'])
            
            # Feedback based on score
            if results['percentage'] >= 80:
                st.success("Excellent work! You've mastered this material.")
            elif results['percentage'] >= 60:
                st.info("Good job! You're on the right track.")
            else:
                st.warning("You might need more review on this material.")
            
            # Detailed results
            st.subheader("Detailed Results")
            for i, detail in enumerate(results['details']):
                with st.expander(f"Question {i+1}: {detail['is_correct']}✓" if detail['is_correct'] else f"Question {i+1}: ✗"):
                    st.write(f"**Question:** {detail['question']}")
                    st.write(f"**Your Answer:** {detail['user_answer']}")
                    st.write(f"**Correct Answer:** {detail['correct_answer']}")
                    if detail['explanation']:
                        st.write(f"**Explanation:** {detail['explanation']}")
            
            # Reset quiz button
            if st.button("Generate New Quiz", key="reset_quiz_button"):
                st.session_state.quiz_questions = []
                st.session_state.quiz_answers = {}
                st.session_state.quiz_results = None
                st.experimental_rerun()