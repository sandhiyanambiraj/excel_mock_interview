import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Add this at the very top
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'   # Suppress TensorFlow warnings

import torch
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
import numpy as np
from collections import Counter

class EvaluationEngine:
    def __init__(self):
        self.similarity_model = None
        self.classifier = None
        self.models_loaded = False
        
    def load_models(self):
        """Load Hugging Face models"""
        try:
            print("🔄 Loading AI models...")
            # Load similarity model
            self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Load sentiment/quality classifier
            self.classifier = pipeline(
                "text-classification",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            
            self.models_loaded = True
            print("✅ AI models loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            self.models_loaded = False

    def evaluate_response(self, question: str, user_response: str, expected_keywords: list, difficulty: str):
        """Evaluate user response using AI models"""
        
        # Basic keyword matching (fallback)
        found_keywords = [kw for kw in expected_keywords if kw.lower() in user_response.lower()]
        keyword_score = len(found_keywords) / len(expected_keywords) if expected_keywords else 0
        
        # Response length analysis
        word_count = len(user_response.split())
        length_score = min(word_count / 50, 1.0)
        
        if self.models_loaded:
            try:
                # Semantic similarity evaluation
                question_embedding = self.similarity_model.encode(question, convert_to_tensor=True)
                response_embedding = self.similarity_model.encode(user_response, convert_to_tensor=True)
                similarity_score = util.pytorch_cos_sim(question_embedding, response_embedding).item()
                
                # Response quality assessment
                quality_result = self.classifier(user_response[:512])
                quality_score = quality_result[0]['score'] if quality_result[0]['label'] == 'POSITIVE' else 1 - quality_result[0]['score']
                
                # Combined score with weights
                final_score = (
                    keyword_score * 0.3 +
                    similarity_score * 0.4 +
                    quality_score * 0.2 +
                    length_score * 0.1
                ) * 100
                
            except Exception as e:
                print(f"AI evaluation failed: {e}")
                final_score = keyword_score * 85
        else:
            final_score = keyword_score * 85
        
        # Generate evaluation text
        evaluation, suggestions = self._generate_feedback(final_score, difficulty)
        
        return {
            "score": round(final_score, 2),
            "evaluation": evaluation,
            "suggestions": suggestions,
            "keywords_found": found_keywords,
            "keywords_missing": list(set(expected_keywords) - set(found_keywords)),
            "confidence": 0.8 if self.models_loaded else 0.5
        }

    def _generate_feedback(self, score: float, difficulty: str):
        """Generate feedback based on score and difficulty"""
        if score >= 85:
            evaluation = "Excellent answer! You demonstrated strong Excel knowledge with specific details."
            suggestions = "Consider providing real-world examples to make your answers more impactful."
        elif score >= 70:
            evaluation = "Good answer. You covered the main points but could add more depth."
            suggestions = "Try to include more technical details and examples from your experience."
        elif score >= 50:
            evaluation = "Fair answer. You touched on basic concepts but missed important details."
            suggestions = "Study this topic more thoroughly and practice explaining it with examples."
        else:
            evaluation = "Your answer needs significant improvement. You missed several key concepts."
            suggestions = "Review the fundamentals of this topic and consider taking an Excel course."
        
        return evaluation, suggestions

# Global instance
evaluation_engine = EvaluationEngine()