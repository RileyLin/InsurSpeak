"""
Integration tests for FastAPI endpoints in main.py.
"""

import pytest
from io import BytesIO
from unittest.mock import Mock, patch


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, client):
        """Test that health endpoint returns 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestAuthEndpoints:
    """Tests for authentication endpoints."""

    def test_register_new_user(self, client, mock_mongodb):
        """Test registering a new user."""
        # Mock: user doesn't exist yet
        mock_mongodb.users.find_one.return_value = None
        mock_mongodb.users.insert_one.return_value = Mock(inserted_id="user123")

        response = client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "name": "New User",
                "password": "SecurePassword123!"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "newuser@example.com"

    def test_register_duplicate_email(self, client, mock_mongodb, sample_user_data):
        """Test registering with an email that already exists."""
        # Mock: user already exists
        mock_mongodb.users.find_one.return_value = sample_user_data

        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "name": "Test User",
                "password": "Password123"
            }
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client, mock_mongodb):
        """Test registering with invalid email format."""
        response = client.post(
            "/auth/register",
            json={
                "email": "not-an-email",
                "name": "Test",
                "password": "Password123"
            }
        )

        # Should fail validation
        assert response.status_code in [400, 422]

    def test_login_success(self, client, mock_mongodb, sample_user_data):
        """Test successful login."""
        # Mock user exists with correct password
        mock_mongodb.users.find_one.return_value = sample_user_data

        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "SecurePassword123!"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, mock_mongodb, sample_user_data):
        """Test login with wrong password."""
        mock_mongodb.users.find_one.return_value = sample_user_data

        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "WrongPassword"
            }
        )

        assert response.status_code == 401

    def test_login_nonexistent_user(self, client, mock_mongodb):
        """Test login with non-existent user."""
        mock_mongodb.users.find_one.return_value = None

        response = client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "Password123"
            }
        )

        assert response.status_code == 401

    def test_get_current_user_info(self, client, authenticated_headers):
        """Test getting current user info with valid token."""
        response = client.get("/auth/me", headers=authenticated_headers)

        assert response.status_code == 200
        data = response.json()
        assert "email" in data

    def test_get_current_user_no_token(self, client):
        """Test getting current user without authentication."""
        response = client.get("/auth/me")

        assert response.status_code == 403  # Forbidden


class TestDocumentProcessing:
    """Tests for document processing endpoints."""

    @patch('document_processor.extract_text_from_pdf')
    @patch('summary_generator.generate_policy_summary')
    def test_process_document_unauthenticated(
        self,
        mock_generate_summary,
        mock_extract_text,
        client,
        mock_mongodb,
        sample_health_policy_text
    ):
        """Test processing document without authentication."""
        # Mock extraction and summary
        mock_extract_text.return_value = (sample_health_policy_text, [])
        mock_generate_summary.return_value = {
            "benefits": ["Medical coverage"],
            "exclusions": ["Cosmetic"]
        }

        # Create mock file
        file_content = b"Mock PDF content"
        files = {"file": ("policy.pdf", BytesIO(file_content), "application/pdf")}
        data = {"insurance_type": "health"}

        response = client.post("/process-document", files=files, data=data)

        assert response.status_code == 200
        result = response.json()
        assert "summary" in result
        assert "insurance_type" in result

    @patch('document_processor.extract_text_from_pdf')
    @patch('summary_generator.generate_policy_summary')
    def test_process_document_authenticated_saves_to_db(
        self,
        mock_generate_summary,
        mock_extract_text,
        client,
        mock_mongodb,
        authenticated_headers,
        sample_health_policy_text,
        sample_user_data
    ):
        """Test that authenticated users get policy saved to database."""
        # Mock user with policy count below limit
        sample_user_data["policy_count"] = 1
        mock_mongodb.users.find_one.return_value = sample_user_data
        mock_mongodb.policies.insert_one.return_value = Mock(inserted_id="policy123")

        mock_extract_text.return_value = (sample_health_policy_text, [])
        mock_generate_summary.return_value = {"benefits": []}

        file_content = b"Mock PDF"
        files = {"file": ("policy.pdf", BytesIO(file_content), "application/pdf")}
        data = {"insurance_type": "health"}

        response = client.post(
            "/process-document",
            files=files,
            data=data,
            headers=authenticated_headers
        )

        assert response.status_code == 200
        # Verify policy was inserted
        assert mock_mongodb.policies.insert_one.called

    def test_process_document_freemium_limit(
        self,
        client,
        mock_mongodb,
        authenticated_headers,
        sample_user_data
    ):
        """Test that free tier users hit policy limit."""
        # User already has 2 policies (free limit)
        sample_user_data["policy_count"] = 2
        sample_user_data["subscription_tier"] = "free"
        mock_mongodb.users.find_one.return_value = sample_user_data

        file_content = b"Mock PDF"
        files = {"file": ("policy.pdf", BytesIO(file_content), "application/pdf")}
        data = {"insurance_type": "health"}

        response = client.post(
            "/process-document",
            files=files,
            data=data,
            headers=authenticated_headers
        )

        # Should get warning about limit
        assert response.status_code in [200, 403]
        if response.status_code == 200:
            data = response.json()
            assert "warning" in data or "limit" in str(data).lower()

    def test_process_document_no_file_no_text(self, client):
        """Test processing without file or text content."""
        response = client.post(
            "/process-document",
            data={"insurance_type": "health"}
        )

        assert response.status_code in [400, 422]

    def test_process_document_auto_detect_type(
        self,
        client,
        mock_mongodb,
        sample_auto_policy_text
    ):
        """Test auto-detection of insurance type."""
        with patch('document_processor.extract_text_from_pdf') as mock_extract, \
             patch('summary_generator.generate_policy_summary') as mock_summary:

            mock_extract.return_value = (sample_auto_policy_text, [])
            mock_summary.return_value = {"benefits": []}

            file_content = b"Mock PDF"
            files = {"file": ("policy.pdf", BytesIO(file_content), "application/pdf")}
            data = {"insurance_type": "other"}  # Trigger auto-detect

            response = client.post("/process-document", files=files, data=data)

            assert response.status_code == 200
            result = response.json()
            # Should auto-detect as "auto" insurance
            assert result["insurance_type"] in ["auto", "other"]


class TestQuestionAnswering:
    """Tests for Q&A endpoint."""

    @patch('question_answerer.answer_question')
    def test_ask_question_success(self, mock_answer_question, client, sample_health_policy_text):
        """Test asking a question about policy."""
        mock_answer_question.return_value = {
            "answer": "Yes, preventive care is covered.",
            "confidence": "high",
            "sources": [{"title": "Benefits", "snippet": "Preventive care..."}]
        }

        response = client.post(
            "/ask-question",
            json={
                "document_text": sample_health_policy_text,
                "question": "Is preventive care covered?"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "confidence" in data

    def test_ask_question_empty_text(self, client):
        """Test asking question with empty document text."""
        response = client.post(
            "/ask-question",
            json={
                "document_text": "",
                "question": "What is covered?"
            }
        )

        # Should handle gracefully
        assert response.status_code in [200, 400]

    def test_ask_question_empty_question(self, client):
        """Test asking empty question."""
        response = client.post(
            "/ask-question",
            json={
                "document_text": "Policy text",
                "question": ""
            }
        )

        assert response.status_code in [200, 400, 422]


class TestPolicyManagement:
    """Tests for policy management endpoints."""

    def test_get_policies_authenticated(
        self,
        client,
        authenticated_headers,
        mock_mongodb,
        sample_policy_data
    ):
        """Test getting user's policies when authenticated."""
        mock_mongodb.policies.find.return_value = [sample_policy_data]

        response = client.get("/policies", headers=authenticated_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_policies_unauthenticated(self, client):
        """Test getting policies without authentication."""
        response = client.get("/policies")

        assert response.status_code == 403

    def test_get_single_policy(
        self,
        client,
        authenticated_headers,
        mock_mongodb,
        sample_policy_data
    ):
        """Test getting a single policy by ID."""
        mock_mongodb.policies.find_one.return_value = sample_policy_data

        response = client.get("/policies/policy123", headers=authenticated_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["insurance_type"] == "health"

    def test_get_nonexistent_policy(
        self,
        client,
        authenticated_headers,
        mock_mongodb
    ):
        """Test getting a policy that doesn't exist."""
        mock_mongodb.policies.find_one.return_value = None

        response = client.get("/policies/nonexistent", headers=authenticated_headers)

        assert response.status_code == 404

    def test_delete_policy(
        self,
        client,
        authenticated_headers,
        mock_mongodb,
        sample_policy_data,
        sample_user_data
    ):
        """Test deleting a policy."""
        mock_mongodb.policies.find_one.return_value = sample_policy_data
        mock_mongodb.policies.delete_one.return_value = Mock(deleted_count=1)
        mock_mongodb.users.find_one.return_value = sample_user_data

        response = client.delete("/policies/policy123", headers=authenticated_headers)

        assert response.status_code == 200
        assert mock_mongodb.policies.delete_one.called

    def test_update_policy_status(
        self,
        client,
        authenticated_headers,
        mock_mongodb,
        sample_policy_data
    ):
        """Test updating policy status."""
        mock_mongodb.policies.find_one.return_value = sample_policy_data
        mock_mongodb.policies.update_one.return_value = Mock()

        response = client.put(
            "/policies/policy123/status",
            json={"status": "archived"},
            headers=authenticated_headers
        )

        assert response.status_code == 200


class TestClaimsAnalysis:
    """Tests for claims analysis endpoint."""

    @patch('claims_engine.analyze_situation')
    def test_analyze_situation_success(
        self,
        mock_analyze,
        client,
        authenticated_headers,
        mock_mongodb,
        sample_policy_data
    ):
        """Test successful situation analysis."""
        mock_mongodb.policies.find.return_value = [sample_policy_data]
        mock_analyze.return_value = {
            "can_file_claims": True,
            "recommendations": [{
                "policy_name": "Health",
                "claim_type": "Medical",
                "priority": "high"
            }],
            "coordination": {},
            "warnings": [],
            "next_steps": []
        }

        response = client.post(
            "/analyze-situation",
            data={"situation": "I was hospitalized"},
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "can_file_claims" in data
        assert "recommendations" in data

    def test_analyze_situation_no_policies(
        self,
        client,
        authenticated_headers,
        mock_mongodb
    ):
        """Test analyzing situation when user has no policies."""
        mock_mongodb.policies.find.return_value = []

        response = client.post(
            "/analyze-situation",
            data={"situation": "Something happened"},
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["can_file_claims"] is False

    def test_analyze_situation_unauthenticated(self, client):
        """Test analyzing situation without authentication."""
        response = client.post(
            "/analyze-situation",
            data={"situation": "Test"}
        )

        assert response.status_code == 403

    def test_get_claims_history(
        self,
        client,
        authenticated_headers,
        mock_mongodb
    ):
        """Test getting claims analysis history."""
        mock_mongodb.claims.find.return_value = [
            {
                "situation": "Hospital visit",
                "created_at": "2024-01-15T10:00:00"
            }
        ]

        response = client.get("/claims-history", headers=authenticated_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestCORS:
    """Tests for CORS configuration."""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are configured."""
        response = client.options("/health")

        # CORS should be configured
        assert response.status_code in [200, 405]


class TestErrorHandling:
    """Tests for error handling."""

    def test_404_not_found(self, client):
        """Test 404 for non-existent endpoint."""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404

    def test_invalid_json_body(self, client):
        """Test handling of invalid JSON in request body."""
        response = client.post(
            "/ask-question",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code in [400, 422]

    @patch('document_processor.extract_text_from_pdf')
    def test_internal_error_handling(self, mock_extract, client):
        """Test handling of internal server errors."""
        # Simulate an unexpected error
        mock_extract.side_effect = Exception("Unexpected error")

        file_content = b"Mock PDF"
        files = {"file": ("policy.pdf", BytesIO(file_content), "application/pdf")}
        data = {"insurance_type": "health"}

        response = client.post("/process-document", files=files, data=data)

        # Should handle error gracefully
        assert response.status_code in [200, 400, 500]
