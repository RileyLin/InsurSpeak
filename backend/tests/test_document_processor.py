"""
Tests for document_processor.py module.
"""

import pytest
from io import BytesIO
from fastapi import UploadFile
from document_processor import (
    extract_text_from_pdf,
    detect_insurance_type,
    extract_entities,
    extract_policy_numbers,
    extract_dates,
    extract_dollar_amounts,
    extract_percentages,
    extract_phone_numbers,
    extract_email_addresses
)


class TestTextExtraction:
    """Tests for PDF text extraction."""

    @pytest.mark.asyncio
    async def test_extract_text_from_valid_pdf(self):
        """Test extracting text from a valid PDF file."""
        # This would require a real PDF file for integration testing
        # For unit testing, we'll mock the UploadFile
        # In a real scenario, you'd use a sample PDF in tests/fixtures/

        # For now, skip or mock
        pytest.skip("Requires sample PDF file - add to tests/fixtures/sample_health.pdf")

    def test_extract_text_handles_empty_file(self):
        """Test handling of empty file."""
        # This would be tested with actual file handling
        pytest.skip("Requires file handling mock")


class TestInsuranceTypeDetection:
    """Tests for insurance type auto-detection."""

    def test_detect_health_insurance(self, sample_health_policy_text):
        """Test detection of health insurance type."""
        detected_type = detect_insurance_type(sample_health_policy_text)
        assert detected_type == "health"

    def test_detect_auto_insurance(self, sample_auto_policy_text):
        """Test detection of auto insurance type."""
        detected_type = detect_insurance_type(sample_auto_policy_text)
        assert detected_type == "auto"

    def test_detect_with_no_keywords(self):
        """Test detection with text containing no insurance keywords."""
        text = "This is a random document with no insurance-related content."
        detected_type = detect_insurance_type(text)
        assert detected_type == "other"

    def test_detect_with_mixed_keywords(self):
        """Test detection with mixed insurance type keywords (highest score wins)."""
        text = """
        This policy covers your vehicle and also includes some health benefits.
        Collision coverage, liability insurance, and medical payments.
        """
        detected_type = detect_insurance_type(text)
        # Should detect as auto since it has more auto-related keywords
        assert detected_type in ["auto", "health"]  # Either is acceptable


class TestEntityExtraction:
    """Tests for entity extraction from policy text."""

    def test_extract_policy_numbers(self, sample_health_policy_text):
        """Test extraction of policy numbers."""
        entities = extract_entities(sample_health_policy_text)
        assert "policy_numbers" in entities
        assert len(entities["policy_numbers"]) > 0
        assert "HLT-2024-123456" in entities["policy_numbers"]

    def test_extract_dates(self, sample_health_policy_text):
        """Test extraction of dates."""
        entities = extract_entities(sample_health_policy_text)
        assert "dates" in entities
        assert len(entities["dates"]) > 0

    def test_extract_dollar_amounts(self, sample_health_policy_text):
        """Test extraction of dollar amounts."""
        entities = extract_entities(sample_health_policy_text)
        assert "amounts" in entities
        assert len(entities["amounts"]) > 0
        # Check for specific amounts
        amounts_str = " ".join(entities["amounts"])
        assert "$1,000" in amounts_str or "1000" in amounts_str

    def test_extract_phone_numbers(self, sample_health_policy_text):
        """Test extraction of phone numbers."""
        entities = extract_entities(sample_health_policy_text)
        assert "phone_numbers" in entities
        # The sample has 1-800-INSURE-ME format
        assert len(entities["phone_numbers"]) > 0

    def test_extract_email_addresses(self, sample_health_policy_text):
        """Test extraction of email addresses."""
        entities = extract_entities(sample_health_policy_text)
        assert "email_addresses" in entities
        assert "claims@healthinsure.com" in entities["email_addresses"]

    def test_extract_from_empty_text(self):
        """Test entity extraction from empty text."""
        entities = extract_entities("")
        assert entities["policy_numbers"] == []
        assert entities["dates"] == []
        assert entities["amounts"] == []

    def test_extract_policy_numbers_variations(self):
        """Test extraction of various policy number formats."""
        text = """
        Policy 1: ABC-123-456
        Policy 2: XYZ123456
        Policy 3: POL-2024-001
        """
        policy_numbers = extract_policy_numbers(text)
        assert len(policy_numbers) >= 2  # At least some should be detected

    def test_extract_dates_various_formats(self):
        """Test extraction of dates in various formats."""
        text = """
        Effective: January 1, 2024
        Expires: 12/31/2024
        Issued: 2024-01-15
        """
        dates = extract_dates(text)
        assert len(dates) >= 2

    def test_extract_dollar_amounts_variations(self):
        """Test extraction of various dollar amount formats."""
        text = """
        Premium: $1,234.56
        Deductible: $1000
        Maximum: $50,000.00
        """
        amounts = extract_dollar_amounts(text)
        assert len(amounts) == 3
        assert "$1,234.56" in amounts or "$1234.56" in amounts

    def test_extract_percentages(self):
        """Test extraction of percentages."""
        text = """
        Coinsurance: 20%
        Coverage rate: 80%
        Interest: 5.5%
        """
        percentages = extract_percentages(text)
        assert len(percentages) == 3
        assert "20%" in percentages

    def test_extract_phone_numbers_formats(self):
        """Test extraction of various phone number formats."""
        text = """
        Call: (800) 123-4567
        Fax: 800-987-6543
        Emergency: 1-888-555-0100
        """
        phones = extract_phone_numbers(text)
        assert len(phones) >= 2

    def test_no_entities_in_plain_text(self):
        """Test that plain text with no entities returns empty lists."""
        text = "This is just plain text with no special entities."
        entities = extract_entities(text)
        assert all(len(v) == 0 for v in entities.values())


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_detect_type_with_unicode_characters(self):
        """Test insurance type detection with unicode characters."""
        text = "健康保険 Health Insurance Coverage médical"
        detected_type = detect_insurance_type(text)
        assert detected_type in ["health", "other"]

    def test_extract_entities_with_malformed_data(self):
        """Test entity extraction with malformed data."""
        text = "$$$$$ 123-ABC-!@#"
        entities = extract_entities(text)
        # Should not crash, may or may not find entities
        assert isinstance(entities, dict)

    def test_very_long_text(self):
        """Test handling of very long policy text."""
        long_text = "Insurance policy details. " * 10000
        detected_type = detect_insurance_type(long_text)
        assert detected_type == "other"  # No specific keywords

    def test_empty_string_handling(self):
        """Test all functions handle empty strings gracefully."""
        assert detect_insurance_type("") == "other"
        assert extract_entities("") is not None
        assert extract_policy_numbers("") == []
        assert extract_dates("") == []
