from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class Question(BaseModel):
    question: str
    difficulty: str
    expected_keywords: List[str]
    follow_up: Optional[str] = None

class EvaluationRequest(BaseModel):
    question: str
    user_response: str
    expected_keywords: List[str]
    difficulty: str

class EvaluationResponse(BaseModel):
    score: float
    evaluation: str
    suggestions: str
    keywords_found: List[str]
    keywords_missing: List[str]
    confidence: float

class InterviewRequest(BaseModel):
    difficulty: str
    num_questions: int

class InterviewResponse(BaseModel):
    questions: List[Question]
    interview_id: str

class FeedbackRequest(BaseModel):
    user_responses: List[dict]
    start_time: datetime
    end_time: datetime

class FeedbackResponse(BaseModel):
    feedback_report: str
    overall_score: float
    strengths: List[str]
    improvements: List[str]