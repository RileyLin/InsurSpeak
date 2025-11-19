from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import json
from typing import Optional, List, Dict, Any
import uvicorn
from datetime import datetime
from bson import ObjectId

from document_processor import (
    process_document, extract_text_from_pdf, detect_insurance_type, extract_entities
)
from term_identifier import identify_terms
from explanation_generator import generate_explanations
from question_answerer import answer_question, identify_question_type, extract_personal_context
from summary_generator import generate_policy_summary
from auth import (
    UserCreate, UserLogin, Token, get_password_hash, verify_password,
    create_access_token, get_current_user, get_current_user_optional,
    validate_password_strength
)
from database import (
    init_database, get_users_collection, get_policies_collection,
    close_database
)

app = FastAPI(
    title="InsurSpeak API",
    description="API for translating insurance jargon to plain language",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("Starting InsurSpeak API...")
    init_database()


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    print("Shutting down InsurSpeak API...")
    close_database()


@app.get("/")
def read_root():
    return {"message": "Welcome to InsurSpeak API v2.0"}


# ============= AUTHENTICATION ENDPOINTS =============

@app.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    """
    Register a new user

    Returns:
        Access token and user data
    """
    users = get_users_collection()
    if users is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available. Please try again later."
        )

    # Check if user already exists
    existing_user = users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Validate password strength
    is_valid, error_msg = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    # Create user
    hashed_password = get_password_hash(user_data.password)
    new_user = {
        "email": user_data.email,
        "name": user_data.name,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_active": True,
        "policy_count": 0,
        "subscription_tier": "free"  # free, premium, enterprise
    }

    result = users.insert_one(new_user)
    user_id = str(result.inserted_id)

    # Create access token
    access_token = create_access_token(
        data={"sub": user_data.email, "user_id": user_id}
    )

    # Prepare user data for response (exclude password)
    user_response = {
        "id": user_id,
        "email": new_user["email"],
        "name": new_user["name"],
        "policy_count": new_user["policy_count"],
        "subscription_tier": new_user["subscription_tier"]
    }

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )


@app.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    Login with email and password

    Returns:
        Access token and user data
    """
    users = get_users_collection()
    if users is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available. Please try again later."
        )

    # Find user
    user = users.find_one({"email": credentials.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Verify password
    if not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    # Create access token
    user_id = str(user["_id"])
    access_token = create_access_token(
        data={"sub": user["email"], "user_id": user_id}
    )

    # Prepare user data for response
    user_response = {
        "id": user_id,
        "email": user["email"],
        "name": user["name"],
        "policy_count": user.get("policy_count", 0),
        "subscription_tier": user.get("subscription_tier", "free")
    }

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )


@app.get("/auth/me")
async def get_current_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current user profile

    Returns:
        User profile data
    """
    return {
        "id": current_user["_id"],
        "email": current_user["email"],
        "name": current_user["name"],
        "policy_count": current_user.get("policy_count", 0),
        "subscription_tier": current_user.get("subscription_tier", "free"),
        "created_at": current_user.get("created_at")
    }


# ============= DOCUMENT PROCESSING ENDPOINTS =============

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
    Answer a specific question about an insurance policy with citations and context
    """
    # Get the answer with citations and metadata
    answer_data = answer_question(question, document_text, insurance_type)

    return JSONResponse(content={
        "question": question,
        "answer": answer_data.get("answer", ""),
        "citations": answer_data.get("citations", []),
        "confidence": answer_data.get("confidence", "medium"),
        "sources": answer_data.get("sources", []),
        "question_type": answer_data.get("question_type", "general"),
        "personal_context": answer_data.get("personal_context", {})
    })

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
