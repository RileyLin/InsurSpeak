# InsurSpeak - Insurance Jargon Translator

InsurSpeak is a web application that translates complex insurance policy language into simple, easy-to-understand terms.

## Features

- Upload or paste insurance policy text
- Highlight and explain complex insurance terms
- Ask questions about specific policy sections
- Get plain-language explanations of insurance jargon
- Focus on workforce benefits insurance (life, disability, health)

## Project Structure

- `/frontend` - React application with Material UI
- `/backend` - FastAPI server with NLP processing and LLM integration

## Getting Started

### Backend Setup

```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix/macOS:
# source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

## Technology Stack

- **Frontend**: React, Material UI, Redux
- **Backend**: Python, FastAPI, OpenAI API
- **Document Processing**: PyPDF2, pdfplumber
- **NLP**: spaCy, NLTK
