import PyPDF2
import pdfplumber
import io
from fastapi import UploadFile
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

async def extract_text_from_pdf(file: UploadFile) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Extract text content and tables from a PDF file

    Returns:
        Tuple of (extracted_text, list_of_tables)
    """
    content = await file.read()
    pdf_text = ""
    tables = []

    # Try with pdfplumber first (better for tables and layout)
    try:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Extract text
                page_text = page.extract_text() or ""
                pdf_text += page_text + "\n\n"

                # Extract tables
                page_tables = page.extract_tables()
                if page_tables:
                    for table_num, table in enumerate(page_tables):
                        tables.append({
                            "page": page_num + 1,
                            "table_number": table_num + 1,
                            "data": table,
                            "rows": len(table),
                            "columns": len(table[0]) if table else 0
                        })

        if pdf_text.strip():
            return pdf_text, tables

    except Exception as e:
        print(f"pdfplumber extraction failed: {e}")

    # Fall back to PyPDF2 if pdfplumber fails
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_text += page.extract_text() + "\n\n"

        if pdf_text.strip():
            return pdf_text, tables

    except Exception as e:
        print(f"PyPDF2 extraction failed: {e}")

    # If all methods fail
    if not pdf_text.strip():
        raise Exception("Failed to extract text from PDF. The PDF may be scanned or image-based. OCR support coming soon.")

    return pdf_text, tables

def process_document(text: str, insurance_type: str) -> Dict[str, Any]:
    """
    Process document text and prepare it for term identification
    """
    # Clean and normalize text
    cleaned_text = clean_text(text)
    
    # Split text into sections
    sections = split_into_sections(cleaned_text)
    
    # Prepare document structure
    document = {
        "text": cleaned_text,
        "sections": sections,
        "insurance_type": insurance_type,
        "metadata": {
            "word_count": len(cleaned_text.split()),
            "section_count": len(sections)
        }
    }
    
    return document

def clean_text(text: str) -> str:
    """
    Clean and normalize text from a document
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove page numbers
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
    
    # Fix common OCR issues
    text = text.replace('|', 'I')
    text = text.replace('0', 'O')
    
    return text.strip()

def split_into_sections(text: str) -> List[Dict[str, Any]]:
    """
    Split document text into logical sections based on headings and formatting
    """
    # Simple section splitting based on common insurance document patterns
    # In a real implementation, this would be more sophisticated
    
    section_headers = [
        "DEFINITIONS", "COVERAGE", "EXCLUSIONS", "LIMITATIONS", 
        "BENEFITS", "ELIGIBILITY", "PREMIUMS", "CLAIMS", "GENERAL PROVISIONS"
    ]
    
    # Initialize with the whole document as a single section
    sections = [{"title": "FULL DOCUMENT", "content": text, "start_index": 0, "end_index": len(text)}]
    
    # Find section boundaries
    for header in section_headers:
        matches = re.finditer(r'(?i)(?:^|\n)\s*(' + re.escape(header) + r')\s*[:.\n]', text)
        for match in matches:
            section_start = match.start()
            section_title = match.group(1)
            
            # Add the section
            sections.append({
                "title": section_title,
                "content": text[section_start:],  # We'll fix the end later
                "start_index": section_start,
                "end_index": len(text)  # Temporary
            })
    
    # Sort sections by start position
    sections.sort(key=lambda x: x["start_index"])
    
    # Fix section end positions
    for i in range(len(sections) - 1):
        sections[i]["end_index"] = sections[i + 1]["start_index"]
        sections[i]["content"] = text[sections[i]["start_index"]:sections[i]["end_index"]]
    
    return sections


def detect_insurance_type(text: str) -> str:
    """
    Auto-detect insurance type from document text

    Returns:
        Insurance type (health, auto, life, disability, travel, home, pet, business, other)
    """
    text_lower = text.lower()

    # Define keywords for each insurance type
    type_keywords = {
        "health": [
            "health insurance", "medical coverage", "hospital", "physician", "prescription",
            "deductible", "copay", "coinsurance", "out-of-pocket", "preventive care",
            "emergency room", "surgery", "diagnosis", "treatment", "healthcare",
            "medicare", "medicaid", "hmo", "ppo", "epo", "in-network", "out-of-network"
        ],
        "auto": [
            "auto insurance", "vehicle", "automobile", "car insurance", "collision",
            "comprehensive", "liability", "property damage", "bodily injury",
            "uninsured motorist", "underinsured motorist", "rental car",
            "roadside assistance", "towing", "windshield", "glass repair"
        ],
        "life": [
            "life insurance", "death benefit", "beneficiary", "beneficiaries",
            "term life", "whole life", "universal life", "cash value",
            "premium payments", "face amount", "policy owner", "insured person",
            "living benefits", "accelerated death benefit", "conversion privilege"
        ],
        "disability": [
            "disability insurance", "income protection", "unable to work",
            "own occupation", "any occupation", "elimination period",
            "benefit period", "residual benefits", "partial disability",
            "total disability", "rehabilitation", "waiver of premium"
        ],
        "travel": [
            "travel insurance", "trip cancellation", "trip interruption",
            "flight delay", "baggage", "luggage", "medical evacuation",
            "travel assistance", "missed connection", "travel accident",
            "emergency medical", "overseas", "abroad", "vacation"
        ],
        "home": [
            "homeowners insurance", "renters insurance", "dwelling",
            "personal property", "liability coverage", "additional living expenses",
            "loss of use", "fire", "theft", "vandalism", "water damage",
            "natural disaster", "earthquake", "flood", "hurricane",
            "replacement cost", "actual cash value", "contents coverage"
        ],
        "pet": [
            "pet insurance", "veterinary", "veterinarian", "animal",
            "dog", "cat", "puppy", "kitten", "illness", "injury",
            "surgery", "diagnostic tests", "prescription medication",
            "hereditary conditions", "congenital conditions", "wellness"
        ],
        "business": [
            "business insurance", "commercial", "general liability",
            "professional liability", "errors and omissions", "e&o",
            "workers compensation", "business interruption", "commercial property",
            "cyber liability", "data breach", "employee", "employer"
        ]
    }

    # Count keyword matches for each type
    type_scores = {}
    for insurance_type, keywords in type_keywords.items():
        score = 0
        for keyword in keywords:
            # Count occurrences of each keyword (case-insensitive)
            count = text_lower.count(keyword)
            score += count

        type_scores[insurance_type] = score

    # Get the type with the highest score
    if max(type_scores.values()) > 0:
        detected_type = max(type_scores, key=type_scores.get)
        print(f"Auto-detected insurance type: {detected_type} (score: {type_scores[detected_type]})")
        return detected_type

    # Default to 'other' if no clear type detected
    return "other"


def extract_entities(text: str) -> Dict[str, Any]:
    """
    Extract structured entities from insurance document

    Returns:
        Dictionary with extracted entities
    """
    entities = {
        "policy_numbers": extract_policy_numbers(text),
        "dates": extract_dates(text),
        "amounts": extract_dollar_amounts(text),
        "percentages": extract_percentages(text),
        "phone_numbers": extract_phone_numbers(text),
        "email_addresses": extract_email_addresses(text)
    }

    return entities


def extract_policy_numbers(text: str) -> List[str]:
    """Extract policy numbers from text"""
    patterns = [
        r'Policy\s+(?:Number|No\.?|#)[\s:]+([A-Z0-9-]+)',
        r'Policy\s+ID[\s:]+([A-Z0-9-]+)',
        r'Member\s+(?:ID|Number)[\s:]+([A-Z0-9-]+)',
        r'Certificate\s+(?:Number|No\.)[\s:]+([A-Z0-9-]+)',
        r'Account\s+(?:Number|No\.)[\s:]+([A-Z0-9-]+)'
    ]

    policy_numbers = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        policy_numbers.extend(matches)

    return list(set(policy_numbers))  # Remove duplicates


def extract_dates(text: str) -> List[str]:
    """Extract dates from text"""
    patterns = [
        r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',  # MM/DD/YYYY or M/D/YY
        r'\b\d{1,2}-\d{1,2}-\d{2,4}\b',  # MM-DD-YYYY or M-D-YY
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',  # Month DD, YYYY
        r'\b\d{4}-\d{2}-\d{2}\b'  # YYYY-MM-DD
    ]

    dates = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        dates.extend(matches)

    return list(set(dates))[:10]  # Return max 10 unique dates


def extract_dollar_amounts(text: str) -> List[str]:
    """Extract dollar amounts from text"""
    pattern = r'\$\s?[\d,]+(?:\.\d{2})?(?:\s?(?:million|billion|thousand))?'
    amounts = re.findall(pattern, text, re.IGNORECASE)

    # Sort by value (descending) and return unique amounts
    unique_amounts = list(set(amounts))
    try:
        def parse_amount(amount_str):
            # Remove $ and commas
            clean = amount_str.replace('$', '').replace(',', '').strip()
            # Handle million/billion/thousand
            multiplier = 1
            if 'million' in clean.lower():
                multiplier = 1000000
                clean = clean.lower().replace('million', '').strip()
            elif 'billion' in clean.lower():
                multiplier = 1000000000
                clean = clean.lower().replace('billion', '').strip()
            elif 'thousand' in clean.lower():
                multiplier = 1000
                clean = clean.lower().replace('thousand', '').strip()
            return float(clean) * multiplier

        unique_amounts.sort(key=parse_amount, reverse=True)
    except:
        pass

    return unique_amounts[:20]  # Return top 20


def extract_percentages(text: str) -> List[str]:
    """Extract percentage values from text"""
    pattern = r'\b\d+(?:\.\d+)?%'
    percentages = re.findall(pattern, text)
    return list(set(percentages))[:20]  # Return max 20 unique percentages


def extract_phone_numbers(text: str) -> List[str]:
    """Extract phone numbers from text"""
    patterns = [
        r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # 555-555-5555 or 5555555555
        r'\(\d{3}\)\s?\d{3}[-.\s]?\d{4}\b'  # (555) 555-5555
    ]

    phone_numbers = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        phone_numbers.extend(matches)

    return list(set(phone_numbers))


def extract_email_addresses(text: str) -> List[str]:
    """Extract email addresses from text"""
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(pattern, text)
    return list(set(emails))
