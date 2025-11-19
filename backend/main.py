from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import json
from typing import Optional, List, Dict, Any
import uvicorn

from document_processor import (
    process_document, extract_text_from_pdf, detect_insurance_type, extract_entities
)
from term_identifier import identify_terms
from explanation_generator import generate_explanations
from question_answerer import answer_question, identify_question_type, extract_personal_context
from summary_generator import generate_policy_summary

app = FastAPI(
    title="InsurSpeak API",
    description="API for translating insurance jargon to plain language",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to InsurSpeak API"}

@app.post("/process-document")
async def process_document_endpoint(
    file: Optional[UploadFile] = File(None),
    text_content: Optional[str] = Form(None),
    insurance_type: str = Form(...)
):
    """
    Process an insurance document (PDF upload or text input)
    and identify complex terms with explanations
    """
    if not file and not text_content:
        raise HTTPException(status_code=400, detail="Either file or text_content must be provided")

    # Extract text and tables
    tables = []
    if file:
        document_text, tables = await extract_text_from_pdf(file)
    else:
        document_text = text_content

    # Auto-detect insurance type if not specified or if "other"
    if not insurance_type or insurance_type == "other":
        insurance_type = detect_insurance_type(document_text)
        print(f"Auto-detected insurance type: {insurance_type}")

    # Extract structured entities (policy numbers, dates, amounts, etc.)
    entities = extract_entities(document_text)

    # Identify complex terms
    identified_terms = identify_terms(document_text, insurance_type)

    # Generate explanations for identified terms
    terms_with_explanations = generate_explanations(identified_terms, insurance_type)

    # Generate structured policy summary
    policy_summary = generate_policy_summary(document_text, insurance_type)

    return JSONResponse(content={
        "original_text": document_text,
        "terms": terms_with_explanations,
        "insurance_type": insurance_type,
        "summary": policy_summary,
        "entities": entities,
        "tables": {
            "count": len(tables),
            "tables": tables[:5]  # Return first 5 tables to avoid huge payloads
        }
    })

@app.post("/ask-question")
async def ask_question_endpoint(
    question: str = Form(...),
    document_text: str = Form(...),
    insurance_type: str = Form(...)
):
    """
    Answer a specific question about an insurance policy
    """
    # Identify the type of question (coverage, recommendation, etc.)
    question_type = identify_question_type(question)
    
    # Extract any personal context from the question
    personal_context = extract_personal_context(question)
    
    # Get the answer
    answer = answer_question(question, document_text, insurance_type)
    
    return JSONResponse(content={
        "question": question,
        "answer": answer,
        "question_type": question_type,
        "personal_context": personal_context
    })

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
