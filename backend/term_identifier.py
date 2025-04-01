import re
import json
import os
from typing import List, Dict, Any

# Dictionary of common insurance terms and their categories
# In a production application, this would be stored in a database
COMMON_INSURANCE_TERMS = {
    "premium": "payment",
    "deductible": "payment",
    "copay": "payment",
    "coinsurance": "payment",
    "out-of-pocket maximum": "payment",
    "beneficiary": "policy",
    "policyholder": "policy",
    "coverage": "policy",
    "claim": "process",
    "exclusion": "coverage",
    "preexisting condition": "medical",
    "waiting period": "policy",
    "rider": "policy",
    "underwriting": "process",
    "actuary": "process",
    "indemnity": "legal",
    "endorsement": "legal",
    "grace period": "policy",
    "guaranteed insurability": "policy",
    "living benefits": "benefit",
    "maturity": "policy",
    "waiver of premium": "benefit",
    "elimination period": "policy",
    "accelerated death benefit": "benefit",
}

# Insurance type specific terms
INSURANCE_TYPE_TERMS = {
    "health": [
        "network provider", "in-network", "out-of-network", "formulary", 
        "prior authorization", "referral", "explanation of benefits", 
        "coordination of benefits", "health maintenance organization", 
        "preferred provider organization", "exclusive provider organization"
    ],
    "life": [
        "cash value", "death benefit", "term life", "whole life", "universal life",
        "variable life", "accidental death", "annuity", "surrender value",
        "paid-up additions", "suicide clause", "contestability period"
    ],
    "disability": [
        "own occupation", "any occupation", "residual disability", "partial disability",
        "total disability", "long-term disability", "short-term disability",
        "presumptive disability", "recurrent disability", "social insurance offset"
    ]
}

def identify_terms(document_text: str, insurance_type: str) -> List[Dict[str, Any]]:
    """
    Identify insurance jargon terms in the document text
    """
    identified_terms = []
    
    # Get terms relevant to this insurance type
    relevant_type_terms = INSURANCE_TYPE_TERMS.get(insurance_type.lower(), [])
    
    # Combine with common terms
    all_terms = list(COMMON_INSURANCE_TERMS.keys()) + relevant_type_terms
    
    # Sort by length (longest first) to avoid substring matches
    all_terms.sort(key=len, reverse=True)
    
    # Find term occurrences in the text
    for term in all_terms:
        # Use word boundaries to find whole terms only
        pattern = r'\b' + re.escape(term) + r'\b'
        for match in re.finditer(pattern, document_text, re.IGNORECASE):
            # Get some context around the term (50 chars before and after)
            start_idx = max(0, match.start() - 50)
            end_idx = min(len(document_text), match.end() + 50)
            context = document_text[start_idx:end_idx]
            
            # Determine category
            category = COMMON_INSURANCE_TERMS.get(term.lower(), "general")
            
            identified_terms.append({
                "term": term,
                "original_text": match.group(0),
                "start_index": match.start(),
                "end_index": match.end(),
                "context": context,
                "category": category,
                "insurance_type": insurance_type
            })
    
    # Advanced term identification using patterns
    identified_terms.extend(identify_complex_terms(document_text, insurance_type))
    
    # Sort terms by their position in the document
    identified_terms.sort(key=lambda x: x["start_index"])
    
    return identified_terms

def identify_complex_terms(document_text: str, insurance_type: str) -> List[Dict[str, Any]]:
    """
    Identify more complex insurance terms and clauses using regex patterns
    """
    complex_terms = []
    
    # Define patterns for complex terms
    patterns = [
        # Numbers with percentage
        (r'\b(\d+(?:\.\d+)?%)\b', "percentage"),
        
        # Dollar amounts
        (r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)', "monetary"),
        
        # Time periods
        (r'\b(\d+\s+(?:day|week|month|year)s?)\b', "time_period"),
        
        # Complex clauses often starting with certain words
        (r'\b(provided that|subject to|notwithstanding|whereas)\b[^.]*\.', "legal_clause")
    ]
    
    # Find matches for each pattern
    for pattern, category in patterns:
        for match in re.finditer(pattern, document_text, re.IGNORECASE):
            # Get context around the match
            start_idx = max(0, match.start() - 50)
            end_idx = min(len(document_text), match.end() + 50)
            context = document_text[start_idx:end_idx]
            
            complex_terms.append({
                "term": match.group(0),
                "original_text": match.group(0),
                "start_index": match.start(),
                "end_index": match.end(),
                "context": context,
                "category": category,
                "insurance_type": insurance_type
            })
    
    return complex_terms
