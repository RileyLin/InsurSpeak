import PyPDF2
import pdfplumber
import io
from fastapi import UploadFile
import re
from typing import Dict, List, Any

async def extract_text_from_pdf(file: UploadFile) -> str:
    """
    Extract text content from a PDF file
    """
    content = await file.read()
    
    # Try with PyPDF2 first
    pdf_text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_text += page.extract_text() + "\n\n"
    except Exception as e:
        print(f"PyPDF2 extraction failed: {e}")
        
        # Fall back to pdfplumber if PyPDF2 fails
        try:
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    pdf_text += page.extract_text() or "" + "\n\n"
        except Exception as e2:
            print(f"pdfplumber extraction failed: {e2}")
            raise Exception("Failed to extract text from PDF")
    
    return pdf_text

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
