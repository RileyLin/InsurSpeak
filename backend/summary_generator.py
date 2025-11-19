"""
summary_generator.py
Generates structured summaries from insurance policy documents using OpenAI
"""

import os
import re
from typing import Dict, List, Any, Optional
from openai import OpenAI

# Initialize OpenAI client
try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    OPENAI_AVAILABLE = True
except:
    OPENAI_AVAILABLE = False
    client = None


def generate_policy_summary(document_text: str, insurance_type: str) -> Dict[str, Any]:
    """
    Generate a comprehensive structured summary of an insurance policy

    Args:
        document_text: The full policy document text
        insurance_type: Type of insurance (health, auto, life, etc.)

    Returns:
        Dictionary containing structured summary data
    """
    if OPENAI_AVAILABLE and client:
        return generate_ai_summary(document_text, insurance_type)
    else:
        return generate_fallback_summary(document_text, insurance_type)


def generate_ai_summary(document_text: str, insurance_type: str) -> Dict[str, Any]:
    """
    Use OpenAI to generate structured summary
    """
    # Truncate text if too long (keep first 10000 chars)
    truncated_text = document_text[:10000] if len(document_text) > 10000 else document_text

    prompt = f"""You are an expert insurance analyst. Analyze the following {insurance_type} insurance policy document and extract structured information.

Policy Document:
{truncated_text}

Extract and organize the following information in JSON format:

{{
  "policyHolder": "Name of policy holder if found, otherwise null",
  "policyNumber": "Policy number if found, otherwise null",
  "coveragePeriod": "Coverage period/dates if found, otherwise null",
  "coverageLimit": "Maximum coverage amount if found, otherwise null",

  "benefits": [
    {{
      "name": "Benefit name",
      "details": "Brief description",
      "amount": "Coverage amount or percentage if specified"
    }}
  ],

  "exclusions": [
    {{
      "name": "Exclusion name",
      "details": "Why this is excluded"
    }}
  ],

  "claimsProcess": {{
    "steps": [
      {{
        "title": "Step title",
        "description": "Step description"
      }}
    ],
    "contact": "Claims contact information",
    "deadline": "Filing deadline information"
  }},

  "costs": {{
    "deductible": "Deductible amount",
    "copay": "Co-pay amount",
    "coinsurance": "Co-insurance percentage",
    "outOfPocketMax": "Out-of-pocket maximum"
  }},

  "rights": [
    {{
      "name": "Right name",
      "description": "Description of this right"
    }}
  ],

  "insights": {{
    "hiddenBenefits": ["List of benefits users might not know about"],
    "watchOut": ["Important limitations or gotchas"],
    "moneySavingTips": ["Tips to maximize benefits and save money"]
  }}
}}

Focus on extracting:
1. WHAT CAN BE CLAIMED (benefits)
2. WHAT CANNOT BE CLAIMED (exclusions)
3. HOW TO FILE CLAIMS (process)
4. COSTS to the policy holder
5. RIGHTS and protections
6. INSIGHTS that would help the user

Return ONLY valid JSON, no markdown formatting or explanation."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert insurance policy analyzer. You extract structured information from policies and return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )

        # Parse the AI response
        ai_response = response.choices[0].message.content

        # Clean up the response if it has markdown formatting
        ai_response = ai_response.strip()
        if ai_response.startswith("```json"):
            ai_response = ai_response[7:]
        if ai_response.startswith("```"):
            ai_response = ai_response[3:]
        if ai_response.endswith("```"):
            ai_response = ai_response[:-3]
        ai_response = ai_response.strip()

        # Parse JSON
        import json
        summary = json.loads(ai_response)

        # Ensure all required fields exist
        summary = validate_and_fill_summary(summary)

        return summary

    except Exception as e:
        print(f"Error generating AI summary: {str(e)}")
        return generate_fallback_summary(document_text, insurance_type)


def generate_fallback_summary(document_text: str, insurance_type: str) -> Dict[str, Any]:
    """
    Generate a basic summary using text parsing when AI is not available
    """
    # Extract basic information using regex
    policy_number = extract_policy_number(document_text)
    amounts = extract_dollar_amounts(document_text)

    # Extract sections
    benefits = extract_section_items(document_text, ["COVERAGE", "BENEFITS", "COVERED SERVICES"])
    exclusions = extract_section_items(document_text, ["EXCLUSIONS", "NOT COVERED", "LIMITATIONS"])

    summary = {
        "policyHolder": None,
        "policyNumber": policy_number,
        "coveragePeriod": None,
        "coverageLimit": amounts[0] if amounts else None,

        "benefits": [
            {"name": benefit, "details": "", "amount": ""}
            for benefit in benefits[:10]  # Limit to 10
        ],

        "exclusions": [
            {"name": exclusion, "details": ""}
            for exclusion in exclusions[:10]  # Limit to 10
        ],

        "claimsProcess": {
            "steps": [
                {"title": "Contact your insurance provider", "description": "Call the number on your insurance card"},
                {"title": "Provide necessary documentation", "description": "Submit required forms and supporting documents"},
                {"title": "Wait for claim processing", "description": "Your claim will be reviewed and processed"}
            ],
            "contact": None,
            "deadline": None
        },

        "costs": {
            "deductible": None,
            "copay": None,
            "coinsurance": None,
            "outOfPocketMax": None
        },

        "rights": [
            {"name": "Right to appeal denied claims", "description": "You can appeal if your claim is denied"},
            {"name": "Right to policy information", "description": "You can request detailed policy information at any time"}
        ],

        "insights": {
            "hiddenBenefits": [
                f"Review your full {insurance_type} policy to discover all available benefits"
            ],
            "watchOut": [
                "Pay attention to exclusions and waiting periods",
                "Understand your deductible and out-of-pocket costs"
            ],
            "moneySavingTips": [
                "Ask questions about your policy to maximize benefits",
                "Keep detailed records of all claims and communications"
            ]
        }
    }

    return summary


def validate_and_fill_summary(summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure summary has all required fields
    """
    default_summary = {
        "policyHolder": None,
        "policyNumber": None,
        "coveragePeriod": None,
        "coverageLimit": None,
        "benefits": [],
        "exclusions": [],
        "claimsProcess": {
            "steps": [],
            "contact": None,
            "deadline": None
        },
        "costs": {
            "deductible": None,
            "copay": None,
            "coinsurance": None,
            "outOfPocketMax": None
        },
        "rights": [],
        "insights": {
            "hiddenBenefits": [],
            "watchOut": [],
            "moneySavingTips": []
        }
    }

    # Merge with defaults
    for key, value in default_summary.items():
        if key not in summary:
            summary[key] = value
        elif isinstance(value, dict) and isinstance(summary[key], dict):
            # Merge nested dicts
            for subkey, subvalue in value.items():
                if subkey not in summary[key]:
                    summary[key][subkey] = subvalue

    return summary


def extract_policy_number(text: str) -> Optional[str]:
    """Extract policy number using regex patterns"""
    patterns = [
        r'Policy\s+(?:Number|No\.?|#)[\s:]+([A-Z0-9-]+)',
        r'Policy\s+ID[\s:]+([A-Z0-9-]+)',
        r'Member\s+ID[\s:]+([A-Z0-9-]+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


def extract_dollar_amounts(text: str) -> List[str]:
    """Extract dollar amounts from text"""
    pattern = r'\$[\d,]+(?:\.\d{2})?'
    amounts = re.findall(pattern, text)

    # Sort by value (descending) and return unique amounts
    unique_amounts = list(set(amounts))
    try:
        unique_amounts.sort(key=lambda x: float(x.replace('$', '').replace(',', '')), reverse=True)
    except:
        pass

    return unique_amounts


def extract_section_items(text: str, section_keywords: List[str]) -> List[str]:
    """
    Extract bullet points or items from sections matching keywords
    """
    items = []

    # Split text into lines
    lines = text.split('\n')
    in_section = False

    for i, line in enumerate(lines):
        line = line.strip()

        # Check if we're entering a relevant section
        if any(keyword in line.upper() for keyword in section_keywords):
            in_section = True
            continue

        # Check if we're leaving the section (new major heading)
        if in_section and line.isupper() and len(line) > 10:
            in_section = False
            continue

        # Extract items from the section
        if in_section and line:
            # Check for bullet points or list items
            if line.startswith(('-', '•', '*', '►')) or re.match(r'^\d+\.', line):
                cleaned_item = re.sub(r'^[-•*►\d.]\s*', '', line)
                if len(cleaned_item) > 5:  # Ignore very short items
                    items.append(cleaned_item[:200])  # Limit length

    return items[:20]  # Return max 20 items
