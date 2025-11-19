"""
Tests for summary_generator.py module.
"""

import pytest
import json
from unittest.mock import Mock, patch
from summary_generator import (
    generate_policy_summary,
    generate_ai_summary,
    clean_json_response,
    fallback_summary_generation
)


class TestSummaryGeneration:
    """Tests for policy summary generation."""

    def test_generate_policy_summary_with_valid_text(self, sample_health_policy_text, mock_openai):
        """Test generating summary from valid policy text."""
        summary = generate_policy_summary(sample_health_policy_text, "health")

        assert summary is not None
        assert isinstance(summary, dict)
        assert "benefits" in summary
        assert "exclusions" in summary
        assert "claimsProcess" in summary
        assert "costs" in summary
        assert "rights" in summary

    def test_generate_policy_summary_with_empty_text(self):
        """Test handling of empty policy text."""
        summary = generate_policy_summary("", "health")
        # Should use fallback
        assert summary is not None
        assert isinstance(summary, dict)

    def test_generate_summary_for_different_types(self, mock_openai):
        """Test summary generation for different insurance types."""
        policy_text = "Auto insurance policy with collision and liability coverage."

        for insurance_type in ["health", "auto", "life", "home"]:
            summary = generate_policy_summary(policy_text, insurance_type)
            assert summary is not None
            assert isinstance(summary, dict)


class TestAISummaryGeneration:
    """Tests for AI-powered summary generation."""

    @patch('openai.ChatCompletion.create')
    def test_generate_ai_summary_success(self, mock_openai_create):
        """Test successful AI summary generation."""
        # Mock successful OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """{
            "benefits": ["Coverage A", "Coverage B"],
            "exclusions": ["Not covered A"],
            "claimsProcess": {"steps": ["Step 1"], "timeline": "30 days"},
            "costs": {"deductible": "$500"},
            "rights": ["Right 1"],
            "insights": ["Insight 1"]
        }"""
        mock_openai_create.return_value = mock_response

        summary = generate_ai_summary("Policy text", "health")

        assert summary is not None
        assert "benefits" in summary
        assert isinstance(summary["benefits"], list)
        assert len(summary["benefits"]) == 2

    @patch('openai.ChatCompletion.create')
    def test_generate_ai_summary_with_markdown_formatting(self, mock_openai_create):
        """Test handling of AI response with markdown code blocks."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """```json
{
    "benefits": ["Test benefit"],
    "exclusions": [],
    "claimsProcess": {},
    "costs": {},
    "rights": [],
    "insights": []
}
```"""
        mock_openai_create.return_value = mock_response

        summary = generate_ai_summary("Policy text", "health")

        assert summary is not None
        assert "benefits" in summary

    @patch('openai.ChatCompletion.create')
    def test_generate_ai_summary_with_invalid_json(self, mock_openai_create):
        """Test handling of invalid JSON from AI."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is not JSON"
        mock_openai_create.return_value = mock_response

        summary = generate_ai_summary("Policy text", "health")

        # Should fall back to default structure
        assert summary is not None
        assert isinstance(summary, dict)

    @patch('openai.ChatCompletion.create')
    def test_generate_ai_summary_api_error(self, mock_openai_create):
        """Test handling of OpenAI API errors."""
        mock_openai_create.side_effect = Exception("API Error")

        summary = generate_ai_summary("Policy text", "health")

        # Should fall back to default structure
        assert summary is not None
        assert isinstance(summary, dict)


class TestJSONCleaning:
    """Tests for JSON response cleaning."""

    def test_clean_json_with_markdown_code_blocks(self):
        """Test cleaning JSON with markdown code blocks."""
        json_str = """```json
{"key": "value"}
```"""
        cleaned = clean_json_response(json_str)
        assert cleaned == '{"key": "value"}'

    def test_clean_json_with_backticks_only(self):
        """Test cleaning JSON with backticks only."""
        json_str = "```\n{\"key\": \"value\"}\n```"
        cleaned = clean_json_response(json_str)
        assert '{"key": "value"}' in cleaned

    def test_clean_json_already_clean(self):
        """Test that already clean JSON is not modified."""
        json_str = '{"key": "value"}'
        cleaned = clean_json_response(json_str)
        assert cleaned == json_str

    def test_clean_json_with_whitespace(self):
        """Test cleaning JSON with extra whitespace."""
        json_str = "  \n  {\"key\": \"value\"}  \n  "
        cleaned = clean_json_response(json_str)
        assert cleaned.strip() == '{"key": "value"}'


class TestFallbackSummary:
    """Tests for fallback summary generation."""

    def test_fallback_summary_structure(self):
        """Test that fallback summary has correct structure."""
        summary = fallback_summary_generation("health")

        assert isinstance(summary, dict)
        assert "benefits" in summary
        assert "exclusions" in summary
        assert "claimsProcess" in summary
        assert "costs" in summary
        assert "rights" in summary
        assert "insights" in summary

        assert isinstance(summary["benefits"], list)
        assert isinstance(summary["exclusions"], list)
        assert isinstance(summary["claimsProcess"], dict)

    def test_fallback_summary_for_health(self):
        """Test fallback summary specific to health insurance."""
        summary = fallback_summary_generation("health")
        benefits_text = " ".join(summary["benefits"])
        assert "medical" in benefits_text.lower() or "health" in benefits_text.lower()

    def test_fallback_summary_for_auto(self):
        """Test fallback summary specific to auto insurance."""
        summary = fallback_summary_generation("auto")
        benefits_text = " ".join(summary["benefits"])
        assert "vehicle" in benefits_text.lower() or "collision" in benefits_text.lower()

    def test_fallback_summary_for_unknown_type(self):
        """Test fallback summary for unknown insurance type."""
        summary = fallback_summary_generation("unknown_type")
        assert summary is not None
        assert isinstance(summary, dict)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_very_long_policy_text(self, mock_openai):
        """Test handling of very long policy text."""
        long_text = "Insurance coverage details. " * 5000  # Very long text
        summary = generate_policy_summary(long_text, "health")
        assert summary is not None

    def test_special_characters_in_text(self, mock_openai):
        """Test handling of special characters."""
        text = "Policy with special chars: @#$%^&*() «» € £ ¥"
        summary = generate_policy_summary(text, "health")
        assert summary is not None

    def test_non_english_text(self, mock_openai):
        """Test handling of non-English text."""
        text = "Póliza de seguro de salud con cobertura médica"
        summary = generate_policy_summary(text, "health")
        assert summary is not None

    @patch('openai.ChatCompletion.create')
    def test_partial_json_response(self, mock_openai_create):
        """Test handling of partial/incomplete JSON from AI."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"benefits": ["Test"]'  # Incomplete JSON
        mock_openai_create.return_value = mock_response

        summary = generate_ai_summary("Policy text", "health")
        assert summary is not None
        assert isinstance(summary, dict)
