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
from claims_engine import analyze_situation
from auth import (
    UserCreate, UserLogin, Token, get_password_hash, verify_password,
    create_access_token, get_current_user, get_current_user_optional,
    validate_password_strength
)
from database import (
    init_database, get_users_collection, get_policies_collection, get_claims_collection,
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
    insurance_type: str = Form(...),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """
    Process an insurance document (PDF upload or text input)
    and identify complex terms with explanations.
    Saves to database if user is authenticated.
    """
    if not file and not text_content:
        raise HTTPException(status_code=400, detail="Either file or text_content must be provided")

    # Extract text and tables
    tables = []
    filename = None
    if file:
        document_text, tables = await extract_text_from_pdf(file)
        filename = file.filename
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

    # Save to database if user is authenticated
    policy_id = None
    if current_user:
        policies = get_policies_collection()
        if policies is not None:
            # Check freemium limits
            user_policy_count = current_user.get("policy_count", 0)
            subscription_tier = current_user.get("subscription_tier", "free")

            # Free tier: max 2 policies
            if subscription_tier == "free" and user_policy_count >= 2:
                # Still process but don't save, return warning
                return JSONResponse(content={
                    "original_text": document_text,
                    "terms": terms_with_explanations,
                    "insurance_type": insurance_type,
                    "summary": policy_summary,
                    "entities": entities,
                    "tables": {
                        "count": len(tables),
                        "tables": tables[:5]
                    },
                    "warning": "You've reached your free policy limit (2 policies). Upgrade to save more policies.",
                    "policy_id": None
                })

            # Save policy
            policy_doc = {
                "user_id": current_user["_id"],
                "insurance_type": insurance_type,
                "filename": filename or "Text Input",
                "original_text": document_text,
                "summary": policy_summary,
                "entities": entities,
                "terms": terms_with_explanations,
                "status": "active",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            result = policies.insert_one(policy_doc)
            policy_id = str(result.inserted_id)

            # Update user's policy count
            users = get_users_collection()
            if users:
                users.update_one(
                    {"_id": ObjectId(current_user["_id"])},
                    {"$inc": {"policy_count": 1}, "$set": {"updated_at": datetime.utcnow()}}
                )

    return JSONResponse(content={
        "original_text": document_text,
        "terms": terms_with_explanations,
        "insurance_type": insurance_type,
        "summary": policy_summary,
        "entities": entities,
        "tables": {
            "count": len(tables),
            "tables": tables[:5]
        },
        "policy_id": policy_id,
        "saved": policy_id is not None
    })

# ============= POLICY MANAGEMENT ENDPOINTS =============

@app.get("/policies")
async def get_user_policies(
    current_user: Dict[str, Any] = Depends(get_current_user),
    status: Optional[str] = None
):
    """
    Get all policies for the current user

    Query params:
        status: Filter by status (active, archived)
    """
    policies = get_policies_collection()
    if policies is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )

    # Build query
    query = {"user_id": current_user["_id"]}
    if status:
        query["status"] = status

    # Get policies sorted by created_at (newest first)
    user_policies = list(policies.find(query).sort("created_at", -1))

    # Convert ObjectId to string and format response
    for policy in user_policies:
        policy["_id"] = str(policy["_id"])
        policy["user_id"] = str(policy["user_id"])
        # Remove large fields from list view
        if "original_text" in policy:
            del policy["original_text"]
        if "terms" in policy:
            policy["terms_count"] = len(policy["terms"])
            del policy["terms"]

    return {"policies": user_policies, "count": len(user_policies)}


@app.get("/policies/{policy_id}")
async def get_policy_by_id(
    policy_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a specific policy by ID
    """
    policies = get_policies_collection()
    if policies is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )

    try:
        policy = policies.find_one({
            "_id": ObjectId(policy_id),
            "user_id": current_user["_id"]
        })
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid policy ID"
        )

    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )

    # Convert ObjectId to string
    policy["_id"] = str(policy["_id"])
    policy["user_id"] = str(policy["user_id"])

    return policy


@app.delete("/policies/{policy_id}")
async def delete_policy(
    policy_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete a policy
    """
    policies = get_policies_collection()
    if policies is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )

    try:
        result = policies.delete_one({
            "_id": ObjectId(policy_id),
            "user_id": current_user["_id"]
        })
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid policy ID"
        )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )

    # Update user's policy count
    users = get_users_collection()
    if users:
        users.update_one(
            {"_id": ObjectId(current_user["_id"])},
            {"$inc": {"policy_count": -1}, "$set": {"updated_at": datetime.utcnow()}}
        )

    return {"message": "Policy deleted successfully"}


@app.put("/policies/{policy_id}/status")
async def update_policy_status(
    policy_id: str,
    new_status: str = Form(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update policy status (active, archived)
    """
    if new_status not in ["active", "archived"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be 'active' or 'archived'"
        )

    policies = get_policies_collection()
    if policies is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )

    try:
        result = policies.update_one(
            {"_id": ObjectId(policy_id), "user_id": current_user["_id"]},
            {"$set": {"status": new_status, "updated_at": datetime.utcnow()}}
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid policy ID"
        )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )

    return {"message": f"Policy status updated to {new_status}"}


# ============= Q&A ENDPOINTS =============

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


# ============= CLAIMS RECOMMENDATION ENDPOINTS =============

@app.post("/analyze-situation")
async def analyze_situation_endpoint(
    situation: str = Form(...),
    incident_date: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    estimated_cost: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Analyze a user's situation and recommend claims from their policies

    THE CORE FEATURE: Describe what happened, get claim recommendations!
    """
    # Get user's active policies
    policies = get_policies_collection()
    if policies is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )

    user_policies = list(policies.find({
        "user_id": current_user["_id"],
        "status": "active"
    }))

    if not user_policies:
        return JSONResponse(content={
            "can_file_claims": False,
            "message": "You don't have any active policies. Please upload your insurance policies first.",
            "recommendations": [],
            "situation": situation
        })

    # Prepare incident details
    incident_details = None
    if any([incident_date, location, estimated_cost, category]):
        incident_details = {
            "date": incident_date,
            "location": location,
            "cost": estimated_cost,
            "category": category
        }

    # Analyze situation and get recommendations
    analysis = analyze_situation(situation, user_policies, incident_details)

    # Save to claims collection for history
    claims_col = get_claims_collection()
    if claims_col:
        claim_record = {
            "user_id": current_user["_id"],
            "situation": situation,
            "incident_details": incident_details,
            "analysis": analysis,
            "policies_checked": [str(p["_id"]) for p in user_policies],
            "created_at": datetime.utcnow(),
            "status": "analyzed"  # analyzed, filed, approved, denied
        }
        claims_col.insert_one(claim_record)

    return JSONResponse(content=analysis)


@app.get("/claims-history")
async def get_claims_history(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get user's claims analysis history
    """
    claims_col = get_claims_collection()
    if claims_col is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )

    # Get claims sorted by newest first
    claims = list(claims_col.find({
        "user_id": current_user["_id"]
    }).sort("created_at", -1).limit(50))

    # Format response
    for claim in claims:
        claim["_id"] = str(claim["_id"])
        claim["user_id"] = str(claim["user_id"])

    return {"claims": claims, "count": len(claims)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
