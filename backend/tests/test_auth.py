"""
Tests for auth.py module.
"""

import pytest
from datetime import timedelta
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    get_current_user,
    get_current_user_optional
)
from fastapi import HTTPException


class TestPasswordHashing:
    """Tests for password hashing and verification."""

    def test_hash_password(self):
        """Test that password hashing works."""
        password = "MySecurePassword123!"
        hashed = hash_password(password)

        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 20  # Bcrypt hashes are long
        assert hashed.startswith("$2b$")  # Bcrypt format

    def test_hash_password_consistency(self):
        """Test that same password produces different hashes (salt)."""
        password = "TestPassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2  # Different due to random salt

    def test_verify_password_correct(self):
        """Test verifying correct password."""
        password = "CorrectPassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test verifying incorrect password."""
        password = "CorrectPassword123"
        wrong_password = "WrongPassword456"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty(self):
        """Test verifying empty password."""
        hashed = hash_password("test")
        assert verify_password("", hashed) is False

    def test_hash_special_characters(self):
        """Test hashing password with special characters."""
        password = "P@ssw0rd!#$%^&*()"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True


class TestJWTTokens:
    """Tests for JWT token creation and decoding."""

    def test_create_access_token(self):
        """Test creating a JWT access token."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20

    def test_create_token_with_expiration(self):
        """Test creating token with custom expiration."""
        data = {"sub": "test@example.com"}
        expires = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=expires)

        assert token is not None
        decoded = decode_access_token(token)
        assert decoded["sub"] == "test@example.com"

    def test_decode_valid_token(self):
        """Test decoding a valid token."""
        email = "user@example.com"
        data = {"sub": email}
        token = create_access_token(data)

        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["sub"] == email

    def test_decode_invalid_token(self):
        """Test decoding an invalid token."""
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token("invalid.token.here")

        assert exc_info.value.status_code == 401

    def test_decode_expired_token(self):
        """Test decoding an expired token."""
        data = {"sub": "test@example.com"}
        # Create token that expires immediately
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))

        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)

        assert exc_info.value.status_code == 401

    def test_token_with_additional_claims(self):
        """Test token with additional custom claims."""
        data = {
            "sub": "user@example.com",
            "role": "admin",
            "tier": "premium"
        }
        token = create_access_token(data)
        decoded = decode_access_token(token)

        assert decoded["sub"] == "user@example.com"
        assert decoded["role"] == "admin"
        assert decoded["tier"] == "premium"


class TestUserAuthentication:
    """Tests for user authentication functions."""

    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self, mock_mongodb, sample_user_data):
        """Test getting current user with valid token."""
        from fastapi.security import HTTPAuthorizationCredentials

        # Mock user in database
        mock_mongodb.users.find_one.return_value = sample_user_data

        # Create token
        token = create_access_token({"sub": sample_user_data["email"]})

        # Create credentials
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

        user = await get_current_user(credentials)

        assert user is not None
        assert user["email"] == sample_user_data["email"]

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token."""
        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid.token"
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_not_found(self, mock_mongodb):
        """Test getting current user when user not in database."""
        from fastapi.security import HTTPAuthorizationCredentials

        # Mock user not found
        mock_mongodb.users.find_one.return_value = None

        token = create_access_token({"sub": "nonexistent@example.com"})
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_optional_with_token(self, mock_mongodb, sample_user_data):
        """Test optional authentication with valid token."""
        from fastapi.security import HTTPAuthorizationCredentials

        mock_mongodb.users.find_one.return_value = sample_user_data

        token = create_access_token({"sub": sample_user_data["email"]})
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

        user = await get_current_user_optional(credentials)

        assert user is not None
        assert user["email"] == sample_user_data["email"]

    @pytest.mark.asyncio
    async def test_get_current_user_optional_without_token(self):
        """Test optional authentication without token."""
        user = await get_current_user_optional(None)
        assert user is None


class TestEdgeCases:
    """Test edge cases and security."""

    def test_hash_very_long_password(self):
        """Test hashing very long password."""
        password = "a" * 1000
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_hash_unicode_password(self):
        """Test hashing password with unicode characters."""
        password = "Pässwörd123你好"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_token_without_sub_claim(self):
        """Test token without 'sub' claim."""
        token = create_access_token({"user": "test@example.com"})  # Wrong key
        # Should still create token but may fail on decode validation
        assert token is not None

    def test_verify_password_with_invalid_hash(self):
        """Test verifying password with invalid hash format."""
        result = verify_password("password", "not-a-valid-bcrypt-hash")
        assert result is False

    def test_create_token_with_empty_data(self):
        """Test creating token with empty data."""
        token = create_access_token({})
        assert token is not None
        # Should still create a valid JWT

    def test_sql_injection_in_password(self):
        """Test that SQL injection attempts in password are safely handled."""
        malicious_password = "' OR '1'='1"
        hashed = hash_password(malicious_password)
        assert verify_password(malicious_password, hashed) is True
        assert verify_password("normal password", hashed) is False
