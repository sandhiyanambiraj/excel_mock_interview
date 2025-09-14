import streamlit as st
import json
import random
import time
from datetime import datetime
import re
from collections import Counter

# Initialize session state
def initialize_session_state():
    if "interview_state" not in st.session_state:
        st.session_state.interview_state = "not_started"
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0
    if "user_responses" not in st.session_state:
        st.session_state.user_responses = []
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "feedback" not in st.session_state:
        st.session_state.feedback = ""
    if "start_time" not in st.session_state:
        st.session_state.start_time = None
    if "evaluation_criteria" not in st.session_state:
        st.session_state.evaluation_criteria = {
            "technical_accuracy": 0,
            "completeness": 0,
            "clarity": 0,
            "efficiency": 0
        }

# Question bank for Excel interview with detailed evaluation criteria
EXCEL_QUESTIONS = [
    {
        "question": "What is the difference between VLOOKUP and HLOOKUP?",
        "difficulty": "beginner",
        "expected_keywords": ["vertical", "horizontal", "lookup", "table", "row", "column", "range", "search"],
        "follow_up": "Can you explain a scenario where HLOOKUP would be more appropriate than VLOOKUP?"
    },
    {
        "question": "How would you use the INDEX-MATCH combination instead of VLOOKUP? What are the advantages?",
        "difficulty": "intermediate",
        "expected_keywords": ["index", "match", "flexible", "left lookup", "dynamic", "column reference", "row reference", "array"],
        "follow_up": "What are the performance implications of using INDEX-MATCH compared to VLOOKUP in large datasets?"
    },
    {
        "question": "Explain how array formulas work in Excel and provide a practical use case.",
        "difficulty": "advanced",
        "expected_keywords": ["array", "CSE", "control shift enter", "multiple calculations", "single formula", "spill range", "dynamic arrays"],
        "follow_up": "How have dynamic arrays in Excel 365 changed the way we work with array formulas?"
    },
    {
        "question": "Describe a situation where you would use pivot tables and how you would create one.",
        "difficulty": "intermediate",
        "expected_keywords": ["data analysis", "summarize", "drag and drop", "fields", "filter", "values", "rows", "columns", "aggregate"],
        "follow_up": "How would you handle data that needs to be updated regularly in a pivot table?"
    },
    {
        "question": "What are Excel macros and how would you create a simple macro to automate a repetitive task?",
        "difficulty": "advanced",
        "expected_keywords": ["vba", "visual basic", "automate", "record macro", "module", "subroutine", "code", "automation"],
        "follow_up": "What are some best practices for writing maintainable VBA code?"
    },
    {
        "question": "How would you use conditional formatting to highlight cells based on specific criteria?",
        "difficulty": "beginner",
        "expected_keywords": ["format", "rules", "conditions", "highlight", "data bars", "color scales", "icon sets", "formula"],
        "follow_up": "Can you create a conditional formatting rule that highlights entire rows based on a cell value?"
    },
    {
        "question": "Explain the purpose of the IFERROR function and provide an example of its usage.",
        "difficulty": "intermediate",
        "expected_keywords": ["error", "handle", "iferror", "iserror", "na", "value", "alternative", "clean data"],
        "follow_up": "When would you choose IFERROR over ISERROR in combination with IF?"
    }
]

def evaluate_response(question, response, question_data):
    """Evaluate user response using keyword matching and response analysis"""
    
    # Keyword matching
    expected_keywords = question_data.get("expected_keywords", [])
    keyword_score = 0
    found_keywords = []
    if expected_keywords:
        found_keywords = [keyword for keyword in expected_keywords if keyword.lower() in response.lower()]
        keyword_score = len(found_keywords) / len(expected_keywords)
    
    # Response length analysis
    word_count = len(response.split())
    length_score = min(word_count / 50, 1.0)  # Cap at 1.0 for 50+ words
    
    # Technical terms check
    technical_terms = ["function", "formula", "cell", "range", "worksheet", "workbook", "data", "analysis", 
                       "vlookup", "hlookup", "pivot", "table", "macro", "vba", "formatting", "conditional"]
    tech_terms_count = sum(1 for term in technical_terms if term in response.lower())
    tech_score = min(tech_terms_count / 5, 1.0)  # Cap at 1.0 for 5+ technical terms
    
    # Calculate final score (weighted average)
    final_score = (keyword_score * 0.5 + length_score * 0.2 + tech_score * 0.3) * 100
    
    # Generate evaluation text based on score
    if final_score >= 85:
        evaluation = "Excellent answer! You demonstrated strong knowledge of Excel concepts with specific details."
        suggestions = "Consider providing even more real-world examples to make your answers more impactful."
    elif final_score >= 70:
        evaluation = "Good answer. You covered the main points but could add more depth to your explanation."
        suggestions = "Try to include more technical details and examples from your experience."
    elif final_score >= 50:
        evaluation = "Fair answer. You touched on the basic concepts but missed some important details."
        suggestions = "Study this topic more thoroughly and practice explaining it with examples."
    else:
        evaluation = "Your answer needs significant improvement. You missed several key concepts."
        suggestions = "Review the fundamentals of this topic and consider taking an Excel course."
    
    return {
        "score": final_score,
        "evaluation": evaluation,
        "suggestions": suggestions,
        "keywords_found": found_keywords,
        "keywords_missing": list(set(expected_keywords) - set(found_keywords))
    }

def generate_feedback_report():
    """Generate overall feedback based on all responses"""
    if not st.session_state.user_responses:
        return "No responses to evaluate."
    
    total_score = sum(response["evaluation"]["score"] for response in st.session_state.user_responses) 
    avg_score = total_score / len(st.session_state.user_responses)
    
    # Calculate scores by difficulty
    difficulty_scores = {"beginner": [], "intermediate": [], "advanced": []}
    for response in st.session_state.user_responses:
        q_difficulty = response.get("difficulty", "unknown")
        if q_difficulty in difficulty_scores:
            difficulty_scores[q_difficulty].append(response["evaluation"]["score"])
    
    avg_beginner = sum(difficulty_scores["beginner"]) / len(difficulty_scores["beginner"]) if difficulty_scores["beginner"] else 0
    avg_intermediate = sum(difficulty_scores["intermediate"]) / len(difficulty_scores["intermediate"]) if difficulty_scores["intermediate"] else 0
    avg_advanced = sum(difficulty_scores["advanced"]) / len(difficulty_scores["advanced"]) if difficulty_scores["advanced"] else 0
    
    # Identify strengths and weaknesses
    all_missing_keywords = []
    all_found_keywords = []
    
    for response in st.session_state.user_responses:
        all_found_keywords.extend(response["evaluation"].get("keywords_found", []))
        all_missing_keywords.extend(response["evaluation"].get("keywords_missing", []))
    
    # Count keyword frequency
    missing_counter = Counter(all_missing_keywords)
    found_counter = Counter(all_found_keywords)
    
    # Determine strengths and areas for improvement
    strengths = [kw for kw, count in found_counter.most_common(5) if count >= 2]
    improvements = [kw for kw, count in missing_counter.most_common(5) if count >= 2]
    
    feedback = f"""
    EXCEL SKILLS ASSESSMENT REPORT
    ==============================
    Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    Total Questions: {len(st.session_state.user_responses)}
    Overall Score: {avg_score:.2f}/100
    
    Performance by Difficulty Level:
    - Beginner: {avg_beginner:.2f}/100
    - Intermediate: {avg_intermediate:.2f}/100
    - Advanced: {avg_advanced:.2f}/100
    
    Detailed Feedback:
    """
    
    for i, response in enumerate(st.session_state.user_responses):
        feedback += f"""
        Question {i+1} ({response.get('difficulty', 'unknown')}): {response['question']}
        Score: {response['evaluation']['score']:.2f}/100
        Evaluation: {response['evaluation']['evaluation']}
        Suggestions: {response['evaluation']['suggestions']}
        """
    
    feedback += f"""
    Overall Assessment:
    {"="*50}
    """
    
    if avg_score >= 85:
        feedback += "Excellent Excel skills! You demonstrate advanced knowledge suitable for senior analyst roles."
        recommendation = "You are well-prepared for positions requiring advanced Excel expertise."
    elif avg_score >= 70:
        feedback += "Strong Excel proficiency. You have a solid understanding of most Excel concepts."
        recommendation = "With some refinement, you could excel in roles requiring Excel expertise."
    elif avg_score >= 50:
        feedback += "Moderate Excel skills. You understand basic concepts but need practice with advanced features."
        recommendation = "Focus on practicing advanced functions like array formulas, pivot tables, and VBA."
    else:
        feedback += "Basic understanding of Excel. You need to strengthen your foundational knowledge."
        recommendation = "Consider taking an Excel course focusing on functions, formulas, and data analysis."
    
    if strengths:
        feedback += f"\n\nStrengths: You demonstrated strong knowledge of {', '.join(strengths)}."
    
    if improvements:
        feedback += f"\n\nAreas for Improvement: Focus on learning more about {', '.join(improvements)}."
    
    feedback += f"\n\nRecommendation: {recommendation}"
    
    return feedback

def display_interview_progress():
    """Display progress bar and question counter"""
    if st.session_state.interview_state == "in_progress" and st.session_state.questions:
        progress = (st.session_state.current_question_index) / len(st.session_state.questions)
        st.progress(progress)
        st.caption(f"Question {st.session_state.current_question_index + 1} of {len(st.session_state.questions)}")

def main():
    st.set_page_config(
        page_title="AI Excel Interviewer",
        page_icon="📊",
        layout="wide"
    )
    
    initialize_session_state()
    
    st.title("🤖 AI-Powered Excel Mock Interviewer")
    st.markdown("---")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Interview Settings")
        difficulty = st.selectbox(
            "Select difficulty level",
            ["Mixed", "Beginner", "Intermediate", "Advanced"],
            index=0
        )
        
        num_questions = st.slider("Number of questions", 3, 7, 5)
        
        if st.button("Configure Interview") and st.session_state.interview_state == "not_started":
            # Filter questions based on difficulty
            if difficulty == "Mixed":
                selected_questions = EXCEL_QUESTIONS
            else:
                selected_questions = [q for q in EXCEL_QUESTIONS if q["difficulty"] == difficulty.lower()]
            
            # Select random questions
            st.session_state.questions = random.sample(
                selected_questions, 
                min(num_questions, len(selected_questions))
            )
            st.success(f"Interview configured with {len(st.session_state.questions)} questions!")
    
    # Main interview interface
    if st.session_state.interview_state == "not_started":
        st.write("""
        ## Welcome to the Excel Mock Interview! 
        
        This AI-powered interview will assess your Excel knowledge through a series of questions
        ranging from basic functions to advanced data analysis techniques.
        
        **How it works:**
        1. Configure your interview settings in the sidebar
        2. Click 'Start Interview' to begin
        3. Answer each question to the best of your ability
        4. Receive a detailed evaluation at the end
        
        The interview will evaluate:
        - Technical accuracy of your answers
        - Completeness of your responses
        - Clarity of explanation
        - Efficiency of suggested solutions
        """)
        
        if st.session_state.questions:
            if st.button("Start Interview", type="primary"):
                st.session_state.interview_state = "in_progress"
                st.session_state.start_time = datetime.now()
                st.rerun()
        else:
            st.info("Please configure your interview settings in the sidebar first.")
    
    elif st.session_state.interview_state == "in_progress":
        display_interview_progress()
        
        if st.session_state.current_question_index < len(st.session_state.questions):
            current_question_data = st.session_state.questions[st.session_state.current_question_index]
            current_question = current_question_data["question"]
            difficulty = current_question_data["difficulty"]
            
            st.subheader(f"Question {st.session_state.current_question_index + 1}")
            st.markdown(f"**Difficulty**: {difficulty.capitalize()}")
            st.markdown(f"**{current_question}**")
            
            user_response = st.text_area(
                "Your answer:", 
                key=f"response_{st.session_state.current_question_index}",
                height=150,
                placeholder="Type your answer here...",
                help="Provide a detailed answer explaining concepts, steps, and if applicable, examples."
            )
            
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("Submit Answer", type="primary"):
                    if user_response.strip():
                        # Evaluate the response
                        evaluation = evaluate_response(current_question, user_response, current_question_data)
                        
                        # Store response and evaluation
                        st.session_state.user_responses.append({
                            "question": current_question,
                            "response": user_response,
                            "difficulty": difficulty,
                            "evaluation": evaluation
                        })
                        
                        # Show evaluation for this question
                        st.session_state.show_evaluation = True
                        st.rerun()
                    else:
                        st.warning("Please provide an answer before submitting.")
            with col2:
                if st.button("I don't know", type="secondary"):
                    # Store empty response with evaluation
                    evaluation = {
                        "score": 0,
                        "evaluation": "Candidate skipped this question.",
                        "suggestions": "Review this topic before your next interview.",
                        "keywords_found": [],
                        "keywords_missing": current_question_data.get("expected_keywords", [])
                    }
                    
                    st.session_state.user_responses.append({
                        "question": current_question,
                        "response": "I don't know",
                        "difficulty": difficulty,
                        "evaluation": evaluation
                    })
                    
                    # Show evaluation for this question
                    st.session_state.show_evaluation = True
                    st.rerun()
            
            # Show evaluation for the current question if available
            if hasattr(st.session_state, 'show_evaluation') and st.session_state.show_evaluation:
                if st.session_state.user_responses and st.session_state.current_question_index < len(st.session_state.user_responses):
                    response_data = st.session_state.user_responses[st.session_state.current_question_index]
                    eval_data = response_data["evaluation"]
                    
                    st.markdown("---")
                    st.subheader("Evaluation")
                    st.markdown(f"**Score: {eval_data['score']:.2f}/100**")
                    
                    # Display score with color coding
                    if eval_data['score'] >= 70:
                        st.success(eval_data['evaluation'])
                    elif eval_data['score'] >= 50:
                        st.warning(eval_data['evaluation'])
                    else:
                        st.error(eval_data['evaluation'])
                    
                    st.info(f"**Suggestions:** {eval_data['suggestions']}")
                    
                    # Show keywords analysis if available
                    if eval_data['keywords_found']:
                        st.markdown("**Keywords identified in your answer:**")
                        st.write(", ".join(eval_data['keywords_found']))
                    
                    if st.button("Next Question", type="primary"):
                        st.session_state.current_question_index += 1
                        st.session_state.show_evaluation = False
                        st.rerun()
        
        else:
            # Interview completed
            st.session_state.interview_state = "completed"
            st.session_state.feedback = generate_feedback_report()
            st.rerun()
    
    elif st.session_state.interview_state == "completed":
        st.balloons()
        st.success("🎉 Interview completed! Here's your detailed feedback:")
        
        # Display feedback report
        st.markdown("### 📋 Excel Skills Assessment Report")
        st.text_area("Full Report", st.session_state.feedback, height=400)
        
        # Display summary metrics
        total_time = datetime.now() - st.session_state.start_time
        st.write(f"**Interview duration:** {total_time.seconds // 60} minutes {total_time.seconds % 60} seconds")
        
        # Create a download button for the feedback
        st.download_button(
            label="Download Feedback Report",
            data=st.session_state.feedback,
            file_name=f"excel_interview_feedback_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )
        
        if st.button("Start New Interview", type="primary"):
            # Reset session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            initialize_session_state()
            st.rerun()

if __name__ == "__main__":
    main()