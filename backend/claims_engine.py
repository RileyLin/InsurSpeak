"""
claims_engine.py
AI-powered claims recommendation engine that matches user situations to policy coverage
"""

import os
import re
from typing import List, Dict, Any, Optional
from openai import OpenAI
from datetime import datetime

# Initialize OpenAI client
try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    OPENAI_AVAILABLE = True
except:
    OPENAI_AVAILABLE = False
    client = None


def analyze_situation(
    situation_description: str,
    user_policies: List[Dict[str, Any]],
    incident_details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze a user's situation and recommend claims from their policies

    Args:
        situation_description: User's description of what happened
        user_policies: List of user's insurance policies with summaries
        incident_details: Optional structured details (date, location, cost, etc.)

    Returns:
        Dictionary with claim recommendations, policy matches, and guidance
    """
    if OPENAI_AVAILABLE and client:
        return ai_analyze_situation(situation_description, user_policies, incident_details)
    else:
        return fallback_analyze_situation(situation_description, user_policies, incident_details)


def ai_analyze_situation(
    situation_description: str,
    user_policies: List[Dict[str, Any]],
    incident_details: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Use OpenAI to analyze situation and match to policies
    """
    # Prepare policy context
    policies_context = prepare_policies_context(user_policies)

    # Build prompt
    prompt = f"""You are an expert insurance claims advisor. A user has experienced a situation and needs to know what claims they can file from their insurance policies.

User's Situation:
{situation_description}

{format_incident_details(incident_details) if incident_details else ""}

User's Insurance Policies:
{policies_context}

Analyze this situation carefully and provide:

1. **Applicable Claims**: Which specific policies cover this situation and what can be claimed
2. **Priority Ranking**: Order claims by value and likelihood of approval
3. **Required Documentation**: What documents/evidence the user needs for each claim
4. **Filing Steps**: Step-by-step process to file each claim
5. **Coverage Coordination**: If multiple policies apply, how they work together
6. **Important Warnings**: Any deadlines, exclusions, or gotchas to watch out for

Format your response as JSON:
{{
  "can_file_claims": true/false,
  "total_potential_value": "estimated total $ amount or range",
  "recommendations": [
    {{
      "policy_name": "Policy name",
      "policy_type": "insurance type",
      "claim_type": "what this claim is for",
      "priority": "high/medium/low",
      "likelihood": "high/medium/low",
      "estimated_amount": "$ amount or percentage",
      "reason": "why this applies",
      "required_docs": ["list", "of", "documents"],
      "filing_steps": ["step 1", "step 2", ...],
      "deadline": "when to file by",
      "notes": "additional important information"
    }}
  ],
  "coordination": {{
    "multiple_policies": true/false,
    "primary_coverage": "which policy pays first",
    "secondary_coverage": "which policy pays second",
    "notes": "how to coordinate"
  }},
  "warnings": [
    "important warning 1",
    "important warning 2"
  ],
  "next_steps": [
    "immediate action 1",
    "immediate action 2"
  ]
}}

If NO policies cover this situation, explain why and suggest alternatives.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert insurance claims advisor. Analyze situations and provide accurate, helpful claims guidance. Always cite specific policy provisions. Return valid JSON only."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2000
        )

        # Parse AI response
        ai_response = response.choices[0].message.content

        # Clean up response
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
        result = json.loads(ai_response)

        # Add metadata
        result["situation"] = situation_description
        result["analyzed_at"] = datetime.utcnow().isoformat()
        result["policies_analyzed"] = len(user_policies)

        return result

    except Exception as e:
        print(f"Error in AI situation analysis: {e}")
        return fallback_analyze_situation(situation_description, user_policies, incident_details)


def fallback_analyze_situation(
    situation_description: str,
    user_policies: List[Dict[str, Any]],
    incident_details: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Fallback analysis using rule-based matching
    """
    situation_lower = situation_description.lower()

    # Simple keyword matching for common scenarios
    recommendations = []

    for policy in user_policies:
        insurance_type = policy.get("insurance_type", "").lower()
        summary = policy.get("summary", {})

        # Health insurance scenarios
        if insurance_type == "health":
            if any(word in situation_lower for word in ["doctor", "hospital", "medical", "surgery", "prescription", "emergency"]):
                recommendations.append({
                    "policy_name": f"{policy.get('filename', 'Health Policy')}",
                    "policy_type": "health",
                    "claim_type": "Medical Expense Claim",
                    "priority": "high",
                    "likelihood": "high" if "emergency" in situation_lower else "medium",
                    "estimated_amount": "Varies based on services",
                    "reason": "Your health insurance may cover medical expenses",
                    "required_docs": ["Medical bills", "Receipts", "Doctor's notes", "Prescription records"],
                    "filing_steps": [
                        "Contact your insurance provider",
                        "Gather all medical bills and receipts",
                        "Complete claim form",
                        "Submit within required timeframe"
                    ],
                    "deadline": "Typically 90-180 days from date of service",
                    "notes": "Check if provider is in-network for better coverage"
                })

        # Auto insurance scenarios
        if insurance_type == "auto":
            if any(word in situation_lower for word in ["car", "accident", "vehicle", "collision", "crash", "damage"]):
                recommendations.append({
                    "policy_name": f"{policy.get('filename', 'Auto Policy')}",
                    "policy_type": "auto",
                    "claim_type": "Auto Damage/Accident Claim",
                    "priority": "high",
                    "likelihood": "high",
                    "estimated_amount": "Varies based on damage",
                    "reason": "Your auto insurance covers vehicle damage and accidents",
                    "required_docs": ["Police report", "Photos of damage", "Other driver's information", "Witness statements"],
                    "filing_steps": [
                        "File police report if applicable",
                        "Document all damage with photos",
                        "Exchange information with other parties",
                        "Contact your insurance company immediately",
                        "Get damage estimate"
                    ],
                    "deadline": "Report within 24-48 hours, file claim within 30 days",
                    "notes": "Do NOT admit fault at the scene"
                })

        # Travel insurance scenarios
        if insurance_type == "travel":
            if any(word in situation_lower for word in ["flight", "delay", "cancel", "baggage", "lost", "trip"]):
                recommendations.append({
                    "policy_name": f"{policy.get('filename', 'Travel Policy')}",
                    "policy_type": "travel",
                    "claim_type": "Travel Disruption Claim",
                    "priority": "medium",
                    "likelihood": "medium",
                    "estimated_amount": "$250-$1000+ depending on delay length",
                    "reason": "Travel insurance may cover delays, cancellations, or lost baggage",
                    "required_docs": ["Boarding passes", "Delay confirmation from airline", "Receipts for expenses", "Baggage claim report"],
                    "filing_steps": [
                        "Get written confirmation of delay/cancellation from airline",
                        "Keep all receipts for additional expenses",
                        "File baggage claim with airline first",
                        "Submit insurance claim with documentation"
                    ],
                    "deadline": "Usually 21-30 days from incident",
                    "notes": "Airline must compensate first, insurance covers the gap"
                })

    if not recommendations:
        return {
            "can_file_claims": False,
            "total_potential_value": "$0",
            "recommendations": [],
            "coordination": {
                "multiple_policies": False,
                "notes": "No matching policies found for this situation"
            },
            "warnings": [
                "None of your current policies appear to cover this situation",
                "Consider reviewing your coverage needs"
            ],
            "next_steps": [
                "Review what happened to see if there are any policy matches we missed",
                "Contact your insurance providers to confirm coverage",
                "Consider purchasing additional coverage for future incidents"
            ],
            "situation": situation_description,
            "analyzed_at": datetime.utcnow().isoformat(),
            "policies_analyzed": len(user_policies)
        }

    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))

    return {
        "can_file_claims": True,
        "total_potential_value": "See individual recommendations",
        "recommendations": recommendations,
        "coordination": {
            "multiple_policies": len(recommendations) > 1,
            "notes": "File claims with each applicable policy" if len(recommendations) > 1 else "Single policy applies"
        },
        "warnings": [
            "Review policy exclusions carefully",
            "File claims as soon as possible to meet deadlines"
        ],
        "next_steps": [
            "Gather required documentation",
            "Contact insurance provider(s)",
            "File claims within required timeframes"
        ],
        "situation": situation_description,
        "analyzed_at": datetime.utcnow().isoformat(),
        "policies_analyzed": len(user_policies)
    }


def prepare_policies_context(policies: List[Dict[str, Any]]) -> str:
    """
    Prepare a readable context of user's policies for AI
    """
    context_parts = []

    for i, policy in enumerate(policies, 1):
        summary = policy.get("summary", {})
        context = f"""
Policy {i}: {policy.get('filename', 'Untitled')}
Type: {policy.get('insurance_type', 'Unknown').capitalize()}
Status: {policy.get('status', 'active').capitalize()}

Coverage Overview:
- Policy Number: {summary.get('policyNumber', 'Not specified')}
- Coverage Period: {summary.get('coveragePeriod', 'Not specified')}
- Coverage Limit: {summary.get('coverageLimit', 'Not specified')}

Key Benefits:
{format_list_items(summary.get('benefits', []), max_items=5)}

Exclusions:
{format_list_items(summary.get('exclusions', []), max_items=3)}

Claims Process:
{format_claims_process(summary.get('claimsProcess', {}))}
"""
        context_parts.append(context)

    return "\n---\n".join(context_parts)


def format_list_items(items: List, max_items: int = 5) -> str:
    """Format list items for readability"""
    if not items:
        return "- Not specified"

    formatted = []
    for item in items[:max_items]:
        if isinstance(item, dict):
            name = item.get('name', str(item))
            details = item.get('details', '')
            formatted.append(f"- {name}" + (f": {details}" if details else ""))
        else:
            formatted.append(f"- {item}")

    if len(items) > max_items:
        formatted.append(f"- ... and {len(items) - max_items} more")

    return "\n".join(formatted)


def format_claims_process(claims_process: Dict[str, Any]) -> str:
    """Format claims process for readability"""
    if not claims_process:
        return "Not specified"

    parts = []
    if claims_process.get('contact'):
        parts.append(f"Contact: {claims_process['contact']}")
    if claims_process.get('deadline'):
        parts.append(f"Deadline: {claims_process['deadline']}")
    if claims_process.get('steps'):
        steps = claims_process['steps']
        if isinstance(steps, list) and steps:
            parts.append("Steps:")
            for i, step in enumerate(steps[:3], 1):
                step_title = step.get('title', step) if isinstance(step, dict) else step
                parts.append(f"  {i}. {step_title}")

    return "\n".join(parts) if parts else "Not specified"


def format_incident_details(incident_details: Dict[str, Any]) -> str:
    """Format incident details for prompt"""
    parts = ["Incident Details:"]

    if incident_details.get('date'):
        parts.append(f"- Date: {incident_details['date']}")
    if incident_details.get('location'):
        parts.append(f"- Location: {incident_details['location']}")
    if incident_details.get('cost'):
        parts.append(f"- Estimated Cost: ${incident_details['cost']}")
    if incident_details.get('category'):
        parts.append(f"- Category: {incident_details['category']}")

    return "\n".join(parts)
