import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow info and warning messages
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN custom operations

import warnings
warnings.filterwarnings('ignore')

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from models import *
from evaluation_engine import evaluation_engine
import random
from datetime import datetime
import uuid

# Lifespan event handler (NEW WAY - replaces @app.on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    evaluation_engine.load_models()
    print("🤖 Backend startup complete - models loaded")
    yield
    # Shutdown code (if any)
    print("🛑 Backend shutting down")

app = FastAPI(
    title="Excel Mock Interviewer API",
    description="AI-powered Excel skills assessment backend",
    version="1.0.0",
    lifespan=lifespan  # Add lifespan here
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Question database
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

@app.get("/")
async def root():
    return {"message": "Excel Mock Interviewer API is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "models_loaded": evaluation_engine.models_loaded}

@app.post("/start_interview", response_model=InterviewResponse)
async def start_interview(request: InterviewRequest):
    """Start a new interview with selected questions"""
    try:
        # Filter questions based on difficulty
        if request.difficulty.lower() == "mixed":
            selected_questions = EXCEL_QUESTIONS
        else:
            selected_questions = [q for q in EXCEL_QUESTIONS if q["difficulty"] == request.difficulty.lower()]
        
        # Select random questions
        questions = random.sample(selected_questions, min(request.num_questions, len(selected_questions)))
        
        return {
            "questions": questions,
            "interview_id": str(uuid.uuid4())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evaluate_response", response_model=EvaluationResponse)
async def evaluate_response(request: EvaluationRequest):
    """Evaluate a single response"""
    try:
        evaluation = evaluation_engine.evaluate_response(
            request.question,
            request.user_response,
            request.expected_keywords,
            request.difficulty
        )
        return evaluation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_feedback", response_model=FeedbackResponse)
async def generate_feedback(request: FeedbackRequest):
    """Generate overall feedback report"""
    try:
        # Calculate overall score
        total_score = sum(response.get("evaluation", {}).get("score", 0) for response in request.user_responses)
        avg_score = total_score / len(request.user_responses) if request.user_responses else 0
        
        # Generate feedback report
        feedback_report = f"Excel Skills Assessment Report\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        feedback_report += f"Overall Score: {avg_score:.2f}/100\n\n"
        
        # Add question-wise feedback
        for i, response in enumerate(request.user_responses):
            eval_data = response.get("evaluation", {})
            feedback_report += f"Question {i+1}: {response.get('question', 'N/A')}\n"
            feedback_report += f"Score: {eval_data.get('score', 0):.2f}/100\n"
            feedback_report += f"Evaluation: {eval_data.get('evaluation', 'No evaluation')}\n"
            feedback_report += f"Suggestions: {eval_data.get('suggestions', 'No suggestions')}\n\n"
        
        # Add overall assessment
        if avg_score >= 85:
            feedback_report += "Excellent Excel skills! You demonstrate advanced knowledge suitable for senior roles."
        elif avg_score >= 70:
            feedback_report += "Good Excel proficiency. With some practice, you could excel in roles requiring Excel expertise."
        else:
            feedback_report += "Basic understanding of Excel. Consider further training and practice before advanced roles."
        
        return {
            "feedback_report": feedback_report,
            "overall_score": avg_score,
            "strengths": ["Good technical knowledge", "Clear explanations"],
            "improvements": ["Add more examples", "Practice advanced functions"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Remove reload=True or use import string format
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)