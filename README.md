# 🤖 AI-Powered Excel Mock Interviewer

A full-stack web application that conducts automated technical interviews for Excel skills assessment using AI-powered evaluation.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0-red.svg)
![Docker](https://img.shields.io/badge/Docker-🐳-lightblue.svg)
![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-yellow.svg)

## 🚀 Features

- **AI-Powered Evaluation**: Uses Hugging Face models for intelligent answer assessment
- **Multi-difficulty Questions**: Beginner, Intermediate, and Advanced Excel questions
- **Real-time Feedback**: Instant evaluation after each question
- **Detailed Reports**: Comprehensive performance analysis with scores and suggestions
- **Dockerized**: Easy deployment with Docker containers
- **RESTful API**: Clean FastAPI backend with automatic documentation

## 📋 Prerequisites

- Docker and Docker Compose
- Or Python 3.9+ (for manual setup)

## 🛠️ Installation

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <your-repository-url>
cd excel-interviewer

# Build and start containers
docker-compose up

# Access the application:
# Frontend: http://localhost:8501
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
Manual Setup
bash
# Backend setup
cd backend
pip install -r requirements.txt
python main.py

# Frontend setup (in new terminal)
cd frontend
pip install -r requirements.txt
streamlit run app.py
🏗️ Project Structure
text
excel-interviewer/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── evaluation_engine.py # AI evaluation logic
│   ├── models.py           # Pydantic models
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Backend container config
├── frontend/
│   ├── app.py             # Streamlit application
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile        # Frontend container config
├── docker-compose.yml     # Multi-container setup
└── README.md             # This file
🎯 How It Works
User starts interview through Streamlit frontend

Frontend requests questions from FastAPI backend

Backend selects appropriate questions based on difficulty

User answers questions in the interface

Backend evaluates responses using AI models:

SentenceTransformer for semantic similarity

DistilBERT for quality assessment

Keyword matching for technical accuracy

System generates comprehensive feedback report

User receives detailed performance analysis

🤖 AI Models Used
all-MiniLM-L6-v2: Sentence transformer for answer similarity scoring

distilbert-base-uncased-finetuned-sst-2-english: Text classification for answer quality assessmen