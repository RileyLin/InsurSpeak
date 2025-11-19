"""
Pytest configuration and shared fixtures for InsurSpeak backend tests.
"""

import pytest
import os
import sys
from typing import Generator
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from database import get_database


@pytest.fixture
def client() -> Generator:
    """
    Create a test client for the FastAPI app.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_openai():
    """
    Mock OpenAI API calls to avoid rate limits and costs during testing.
    """
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = """{
        "benefits": ["Medical coverage", "Prescription drugs"],
        "exclusions": ["Cosmetic procedures", "Experimental treatments"],
        "claimsProcess": {
            "steps": ["Call provider", "Submit claim form"],
            "timeline": "30 days",
            "requiredDocuments": ["Medical records", "Receipts"]
        },
        "costs": {
            "deductible": "$1,000",
            "copay": "$25",
            "outOfPocketMax": "$5,000"
        },
        "rights": ["Right to appeal", "Right to second opinion"],
        "insights": ["Good coverage for preventive care"]
    }"""

    with patch('openai.ChatCompletion.create', return_value=mock_response):
        yield mock_response


@pytest.fixture
def mock_mongodb():
    """
    Mock MongoDB database for testing without requiring a real database.
    """
    mock_db = Mock()
    mock_collection = Mock()

    # Mock users collection
    mock_db.users = Mock()
    mock_db.users.find_one = Mock(return_value=None)
    mock_db.users.insert_one = Mock()
    mock_db.users.update_one = Mock()

    # Mock policies collection
    mock_db.policies = Mock()
    mock_db.policies.find = Mock(return_value=[])
    mock_db.policies.find_one = Mock(return_value=None)
    mock_db.policies.insert_one = Mock()
    mock_db.policies.update_one = Mock()
    mock_db.policies.delete_one = Mock()

    # Mock claims collection
    mock_db.claims = Mock()
    mock_db.claims.find = Mock(return_value=[])
    mock_db.claims.insert_one = Mock()

    with patch('database.get_database', return_value=mock_db):
        yield mock_db


@pytest.fixture
def sample_health_policy_text():
    """
    Sample health insurance policy text for testing.
    """
    return """
    COMPREHENSIVE HEALTH INSURANCE POLICY

    Policy Number: HLT-2024-123456
    Effective Date: January 1, 2024

    COVERAGE SUMMARY:
    This policy provides comprehensive health insurance coverage including:
    - Inpatient and outpatient hospital services
    - Physician services and consultations
    - Prescription drug coverage
    - Preventive care and wellness visits
    - Emergency care

    BENEFITS:
    1. Medical Services: Coverage for medically necessary services
    2. Annual Deductible: $1,000 per individual
    3. Out-of-Pocket Maximum: $5,000 per individual
    4. Copayment: $25 per office visit

    EXCLUSIONS:
    The following services are NOT covered:
    - Cosmetic procedures
    - Experimental or investigational treatments
    - Services not deemed medically necessary

    CLAIMS PROCESS:
    1. Obtain services from in-network provider
    2. Provider submits claim directly to insurer
    3. You pay copayment at time of service
    4. Claims processed within 30 days

    For questions, call: 1-800-INSURE-ME
    Email: claims@healthinsure.com
    """


@pytest.fixture
def sample_auto_policy_text():
    """
    Sample auto insurance policy text for testing.
    """
    return """
    AUTO INSURANCE POLICY

    Policy Number: AUTO-2024-789012
    Effective Date: March 15, 2024

    COVERAGE:
    - Liability Coverage: $100,000/$300,000/$50,000
    - Collision Coverage: Actual Cash Value (ACV)
    - Comprehensive Coverage: ACV
    - Uninsured Motorist: $100,000/$300,000

    DEDUCTIBLES:
    - Collision: $500
    - Comprehensive: $250

    EXCLUSIONS:
    - Intentional damage
    - Racing or competitive events
    - Commercial use

    CLAIMS:
    Report accidents within 24 hours to: 1-800-AUTO-CLAIM
    """


@pytest.fixture
def sample_user_data():
    """
    Sample user data for testing authentication and authorization.
    """
    return {
        "email": "test@example.com",
        "name": "Test User",
        "password": "SecurePassword123!",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS.d7RW8O",  # "SecurePassword123!"
        "policy_count": 0,
        "subscription_tier": "free"
    }


@pytest.fixture
def sample_policy_data():
    """
    Sample policy data for testing policy management.
    """
    return {
        "insurance_type": "health",
        "policy_name": "Comprehensive Health Policy",
        "document_text": "Sample policy text...",
        "summary": {
            "benefits": ["Medical coverage"],
            "exclusions": ["Cosmetic procedures"]
        },
        "entities": {
            "policy_numbers": ["HLT-2024-123456"],
            "dates": ["January 1, 2024"],
            "amounts": ["$1,000", "$5,000"]
        },
        "status": "active"
    }


@pytest.fixture
def authenticated_headers(client, mock_mongodb, sample_user_data):
    """
    Create authenticated headers with a valid JWT token.
    """
    # Mock user exists in database
    mock_mongodb.users.find_one.return_value = sample_user_data

    # Register and login
    response = client.post(
        "/auth/login",
        json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
    )

    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    # If login fails, create a mock token
    from auth import create_access_token
    token = create_access_token({"sub": sample_user_data["email"]})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def reset_environment():
    """
    Reset environment variables before each test.
    """
    # Save original environment
    original_env = os.environ.copy()

    # Set test environment variables
    os.environ["MONGODB_URL"] = "mongodb://localhost:27017/insurspeak_test"
    os.environ["OPENAI_API_KEY"] = "test-key-mock"
    os.environ["SECRET_KEY"] = "test-secret-key-for-jwt-signing"

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)
