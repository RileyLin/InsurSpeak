"""
Tests for claims_engine.py module.
"""

import pytest
from unittest.mock import Mock, patch
from claims_engine import (
    analyze_situation,
    prepare_policies_context,
    extract_situation_keywords,
    rule_based_matching
)


class TestSituationAnalysis:
    """Tests for situation analysis and claim recommendations."""

    @patch('openai.ChatCompletion.create')
    def test_analyze_situation_with_single_policy(self, mock_openai_create, sample_policy_data):
        """Test analyzing situation with single policy."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """{
            "can_file_claims": true,
            "recommendations": [{
                "policy_name": "Health Policy",
                "claim_type": "Medical Claim",
                "priority": "high",
                "likelihood": "very_likely",
                "estimated_amount": "$500-1000",
                "required_documents": ["Medical records"],
                "filing_steps": ["Step 1"],
                "deadline": "30 days",
                "notes": "Strong case"
            }],
            "coordination": {},
            "warnings": [],
            "next_steps": ["File claim"]
        }"""
        mock_openai_create.return_value = mock_response

        situation = "I was hospitalized for an emergency surgery"
        policies = [sample_policy_data]

        result = analyze_situation(situation, policies)

        assert result is not None
        assert "can_file_claims" in result
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0

    @patch('openai.ChatCompletion.create')
    def test_analyze_situation_with_multiple_policies(self, mock_openai_create):
        """Test analyzing situation with multiple policies (coordination)."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """{
            "can_file_claims": true,
            "recommendations": [
                {
                    "policy_name": "Health Policy",
                    "claim_type": "Medical Claim",
                    "priority": "high",
                    "likelihood": "very_likely",
                    "estimated_amount": "$1000",
                    "required_documents": ["Medical records"],
                    "filing_steps": ["File with health first"],
                    "deadline": "30 days",
                    "notes": "Primary coverage"
                },
                {
                    "policy_name": "Auto Policy",
                    "claim_type": "Medical Payments",
                    "priority": "medium",
                    "likelihood": "likely",
                    "estimated_amount": "$500",
                    "required_documents": ["Police report"],
                    "filing_steps": ["File after health claim"],
                    "deadline": "60 days",
                    "notes": "Secondary coverage"
                }
            ],
            "coordination": {
                "primary_policy": "Health Policy",
                "filing_order": ["Health", "Auto"]
            },
            "warnings": ["File health claim first"],
            "next_steps": ["Gather medical records"]
        }"""
        mock_openai_create.return_value = mock_response

        situation = "Car accident with injuries"
        policies = [
            {"insurance_type": "health", "policy_name": "Health Policy"},
            {"insurance_type": "auto", "policy_name": "Auto Policy"}
        ]

        result = analyze_situation(situation, policies)

        assert result["can_file_claims"] is True
        assert len(result["recommendations"]) == 2
        assert "coordination" in result

    def test_analyze_situation_no_policies(self):
        """Test analyzing situation with no policies."""
        situation = "I need to file a claim"
        policies = []

        result = analyze_situation(situation, policies)

        assert result is not None
        assert result["can_file_claims"] is False
        assert len(result["recommendations"]) == 0

    def test_analyze_situation_empty_description(self):
        """Test analyzing empty situation description."""
        situation = ""
        policies = [{"insurance_type": "health"}]

        result = analyze_situation(situation, policies)

        # Should handle gracefully
        assert result is not None


class TestPolicyContextPreparation:
    """Tests for preparing policy context for AI analysis."""

    def test_prepare_single_policy_context(self):
        """Test preparing context for single policy."""
        policies = [{
            "insurance_type": "health",
            "policy_name": "Health Plan",
            "summary": {
                "benefits": ["Medical coverage"],
                "exclusions": ["Cosmetic"]
            }
        }]

        context = prepare_policies_context(policies)

        assert "Health Plan" in context
        assert "Medical coverage" in context

    def test_prepare_multiple_policies_context(self):
        """Test preparing context for multiple policies."""
        policies = [
            {"insurance_type": "health", "policy_name": "Health Plan"},
            {"insurance_type": "auto", "policy_name": "Auto Plan"}
        ]

        context = prepare_policies_context(policies)

        assert "Health Plan" in context
        assert "Auto Plan" in context

    def test_prepare_context_with_missing_summary(self):
        """Test preparing context when policy lacks summary."""
        policies = [{"insurance_type": "health", "policy_name": "Basic Plan"}]

        context = prepare_policies_context(policies)

        assert "Basic Plan" in context

    def test_prepare_empty_policies_list(self):
        """Test preparing context with empty policies list."""
        context = prepare_policies_context([])
        assert context == ""


class TestKeywordExtraction:
    """Tests for extracting keywords from situation description."""

    def test_extract_keywords_from_medical_situation(self):
        """Test extracting keywords from medical situation."""
        situation = "I was hospitalized for emergency surgery after an accident"
        keywords = extract_situation_keywords(situation)

        assert "hospitalized" in keywords or "hospital" in keywords
        assert "surgery" in keywords
        assert "emergency" in keywords
        assert "accident" in keywords

    def test_extract_keywords_filters_stop_words(self):
        """Test that common stop words are filtered out."""
        situation = "I was in the hospital and the doctor said I need surgery"
        keywords = extract_situation_keywords(situation)

        # Stop words should be removed
        assert "was" not in keywords
        assert "the" not in keywords
        assert "and" not in keywords

    def test_extract_keywords_from_short_text(self):
        """Test extracting keywords from short text."""
        situation = "Car accident"
        keywords = extract_situation_keywords(situation)

        assert len(keywords) >= 1
        assert "car" in keywords or "accident" in keywords


class TestRuleBasedMatching:
    """Tests for rule-based claim matching fallback."""

    def test_rule_based_health_claim(self):
        """Test rule-based matching for health situation."""
        situation = "I went to the hospital for treatment"
        policies = [{"insurance_type": "health", "policy_name": "Health Plan"}]

        recommendations = rule_based_matching(situation, policies)

        assert len(recommendations) > 0
        assert recommendations[0]["policy_name"] == "Health Plan"
        assert "medical" in recommendations[0]["claim_type"].lower() or \
               "health" in recommendations[0]["claim_type"].lower()

    def test_rule_based_auto_claim(self):
        """Test rule-based matching for auto situation."""
        situation = "My car was damaged in a collision"
        policies = [{"insurance_type": "auto", "policy_name": "Auto Insurance"}]

        recommendations = rule_based_matching(situation, policies)

        assert len(recommendations) > 0
        assert recommendations[0]["policy_name"] == "Auto Insurance"

    def test_rule_based_travel_claim(self):
        """Test rule-based matching for travel situation."""
        situation = "My flight was delayed and I missed my connection"
        policies = [{"insurance_type": "travel", "policy_name": "Travel Insurance"}]

        recommendations = rule_based_matching(situation, policies)

        assert len(recommendations) > 0
        assert recommendations[0]["policy_name"] == "Travel Insurance"

    def test_rule_based_no_match(self):
        """Test rule-based matching when no keywords match."""
        situation = "Something happened"
        policies = [{"insurance_type": "health", "policy_name": "Health Plan"}]

        recommendations = rule_based_matching(situation, policies)

        # Should still return something, but with low likelihood
        assert len(recommendations) >= 0

    def test_rule_based_multiple_policies(self):
        """Test rule-based matching with multiple applicable policies."""
        situation = "Car accident with injuries"
        policies = [
            {"insurance_type": "health", "policy_name": "Health"},
            {"insurance_type": "auto", "policy_name": "Auto"}
        ]

        recommendations = rule_based_matching(situation, policies)

        # Should match both
        assert len(recommendations) >= 2


class TestIncidentDetails:
    """Tests for handling optional incident details."""

    @patch('openai.ChatCompletion.create')
    def test_analyze_with_incident_date(self, mock_openai_create, sample_policy_data):
        """Test analysis with incident date provided."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """{
            "can_file_claims": true,
            "recommendations": [],
            "coordination": {},
            "warnings": [],
            "next_steps": []
        }"""
        mock_openai_create.return_value = mock_response

        situation = "Hospital visit"
        incident_details = {
            "incident_date": "2024-01-15",
            "location": "New York",
            "amount": "$1000"
        }

        result = analyze_situation(situation, [sample_policy_data], incident_details)

        assert result is not None

    @patch('openai.ChatCompletion.create')
    def test_analyze_with_location(self, mock_openai_create, sample_policy_data):
        """Test analysis with location provided."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"can_file_claims": false, "recommendations": [], "coordination": {}, "warnings": [], "next_steps": []}'
        mock_openai_create.return_value = mock_response

        incident_details = {"location": "California"}
        result = analyze_situation("Incident", [sample_policy_data], incident_details)

        assert result is not None


class TestEdgeCases:
    """Test edge cases and error handling."""

    @patch('openai.ChatCompletion.create')
    def test_analyze_with_api_error(self, mock_openai_create):
        """Test handling of OpenAI API errors (should fall back to rule-based)."""
        mock_openai_create.side_effect = Exception("API Error")

        situation = "Hospital visit"
        policies = [{"insurance_type": "health", "policy_name": "Health"}]

        result = analyze_situation(situation, policies)

        # Should fall back to rule-based matching
        assert result is not None
        assert isinstance(result, dict)

    @patch('openai.ChatCompletion.create')
    def test_analyze_with_invalid_json_response(self, mock_openai_create):
        """Test handling of invalid JSON from OpenAI."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Not valid JSON"
        mock_openai_create.return_value = mock_response

        result = analyze_situation("Situation", [{"insurance_type": "health"}])

        # Should fall back
        assert result is not None

    def test_very_long_situation_description(self):
        """Test handling of very long situation description."""
        situation = "I had an accident " * 1000
        policies = [{"insurance_type": "health"}]

        result = analyze_situation(situation, policies)

        assert result is not None

    def test_special_characters_in_situation(self):
        """Test handling of special characters in situation."""
        situation = "Accident @ 123 Main St. - $5,000 damage! #urgent"
        policies = [{"insurance_type": "auto"}]

        result = analyze_situation(situation, policies)

        assert result is not None

    def test_non_english_situation(self):
        """Test handling of non-English situation description."""
        situation = "Tuve un accidente de coche"
        policies = [{"insurance_type": "auto"}]

        result = analyze_situation(situation, policies)

        assert result is not None
