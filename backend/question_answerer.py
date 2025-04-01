import os
import re
import sys
import requests
import json
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def answer_question(question: str, document_text: str, insurance_type: str) -> str:
    """
    Generate an answer to a user's question about their insurance policy
    """
    try:
        # Identify the type of question (coverage, recommendation, interpretation)
        question_type = identify_question_type(question)
        
        # Extract personal context from the question
        personal_context = extract_personal_context(question)
        
        # For real OpenAI API implementation
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            return call_openai_api(question, document_text, insurance_type, question_type, personal_context)
        else:
            # Fallback to mock if no API key
            return mock_answer(question, document_text, insurance_type, question_type)
            
    except Exception as e:
        print(f"Error generating answer: {e}")
        import traceback
        traceback.print_exc()
        return "I'm sorry, I couldn't process your question. Please try again or rephrase your question."

def call_openai_api(question: str, document_text: str, insurance_type: str, question_type: str, personal_context: Dict[str, Any]) -> str:
    """
    Call the OpenAI API to generate an answer
    """
    # Prepare the prompt
    prompt = create_question_prompt(question, document_text, insurance_type, question_type, personal_context)
    
    # API endpoint
    api_url = "https://api.openai.com/v1/chat/completions"
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Headers with proper authentication
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Request body
    data = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are an insurance expert assistant that explains complex insurance concepts in simple terms."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,
        "max_tokens": 500
    }
    
    try:
        print(f"Calling OpenAI API with model: gpt-4o")
        response = requests.post(api_url, headers=headers, json=data)
        
        # Check for errors
        response.raise_for_status()
        
        # Parse the response
        response_data = response.json()
        
        # Extract the generated text
        if "choices" in response_data and len(response_data["choices"]) > 0:
            answer = response_data["choices"][0]["message"]["content"]
            return answer
        else:
            return "No answer was generated. Please try again."
    
    except requests.exceptions.HTTPError as http_err:
        error_message = f"HTTP error: {http_err}"
        try:
            error_data = response.json()
            if "error" in error_data:
                error_message = f"API error: {error_data['error']['message']}"
        except:
            pass
        print(error_message)
        return f"Error: {error_message}"
    
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return f"Error: {str(e)}"

def create_question_prompt(question: str, document_text: str, insurance_type: str, question_type: str, personal_context: Dict[str, Any]) -> str:
    """
    Create a prompt for the LLM to answer the question based on the document and question type
    """
    # Truncate document text if it's too long
    max_text_length = 4000  # Adjust based on token limits
    truncated_text = document_text[:max_text_length] if len(document_text) > max_text_length else document_text
    
    base_prompt = f"""
    You are an insurance expert assistant helping a user understand their insurance policy. Your goal is to explain complex insurance concepts in simple terms.

    User's insurance policy type: {insurance_type}
    
    Relevant policy text:
    {truncated_text}

    User question: {question}
    """
    
    # Add personal context to the prompt
    if personal_context:
        base_prompt += f"""
        User's personal context:
        {', '.join(f'{key}: {value}' for key, value in personal_context.items())}
        """
    
    # Customize prompt based on question type
    if question_type == "recommendation":
        base_prompt += """
        This appears to be a personalized recommendation question. Please:
        1. Consider the user's individual situation as implied in their question
        2. Explain how various factors (age, health status, family situation, etc.) might affect this decision
        3. Highlight the pros and cons of different options
        4. Suggest what questions they should ask themselves to make the best decision
        5. End with a balanced recommendation but emphasize they should consult with a licensed insurance advisor
        """
    elif question_type == "coverage":
        base_prompt += """
        This appears to be a coverage question. Please:
        1. Clearly state what the policy seems to cover and what it doesn't
        2. Highlight any conditions, limitations, or exclusions that apply
        3. Explain any relevant deductibles, copays, or out-of-pocket costs
        4. Mention if there are any circumstances where coverage might change
        5. Note if there are any ambiguities in the policy that would require clarification
        """
    elif question_type == "comparison":
        base_prompt += """
        This appears to be a comparison question. Please:
        1. Clearly outline the key differences between the options mentioned
        2. Compare costs, coverage, limitations, and benefits objectively
        3. Highlight scenarios where one option might be better than another
        4. Consider different user circumstances in your comparison
        5. Provide a balanced assessment rather than strongly favoring one option
        """
    elif question_type == "definition":
        base_prompt += """
        This appears to be a question about defining a term or concept. Please:
        1. Provide a clear, simple definition in everyday language
        2. Explain why this term matters in the context of insurance
        3. Give a practical example of how this concept works in real life
        4. Note any variations in how this term might be used across different policies
        """
    
    base_prompt += """
    Provide a clear, straightforward answer that:
    1. Directly addresses the user's question
    2. Uses simple language (aim for 8th-grade reading level)
    3. Explains any technical terms you need to use
    4. Does NOT provide legal advice or definitive coverage determinations
    5. Includes appropriate disclaimers when the answer requires interpretation

    If the answer cannot be determined from the policy text provided, explain what additional information would be needed.
    """
    
    return base_prompt

def mock_answer(question: str, document_text: str, insurance_type: str, question_type: str) -> str:
    """
    Generate a mock answer for testing purposes without using the OpenAI API
    """
    question_lower = question.lower()
    
    # Deductible questions
    if "deductible" in question_lower:
        return "According to your policy, your annual deductible is $1,500 for an individual and $3,000 for a family. This means you'll need to pay this amount out of pocket before your insurance coverage begins to pay for eligible medical expenses."
    
    # Copay questions
    elif "copay" in question_lower or "co-pay" in question_lower:
        return "Based on your policy, you have different copayments depending on the service: $30 for primary care visits, $50 for specialist visits, $250 for emergency room visits (waived if admitted), and varying copays for prescription medications ($15 for generic, $40 for preferred brands, and $75 for non-preferred brands)."
    
    # Coverage questions
    elif "cover" in question_lower or "coverage" in question_lower:
        if "prescription" in question_lower or "medication" in question_lower:
            return "Your policy covers prescription medications with the following copayments: $15 for generic medications, $40 for preferred brand medications, $75 for non-preferred brand medications, and 30% coinsurance (up to $250 maximum) for specialty medications."
        elif "specialist" in question_lower:
            return "Specialist visits are covered with a $50 copayment per visit."
        elif "preventive" in question_lower or "prevention" in question_lower:
            return "Preventive care services are covered at 100% with no deductible. This includes routine check-ups, vaccinations, and screenings as recommended by standard medical guidelines."
        else:
            return "Your policy provides coverage for hospitalization (80% after deductible), emergency services ($250 copay, waived if admitted), physician services, and prescription drugs, subject to the specific limitations and exclusions outlined in the policy."
    
    # Out-of-pocket maximum questions
    elif "out of pocket" in question_lower or "maximum" in question_lower:
        return "Your policy has an out-of-pocket maximum of $6,000 for an individual and $12,000 for a family. Once you reach this amount in a calendar year, your eligible medical expenses will be covered at 100% for the remainder of the year. This maximum includes your deductibles, copayments, and coinsurance."
    
    # Exclusion questions
    elif "exclusion" in question_lower or "not covered" in question_lower:
        return "Your policy does not cover: 1) Cosmetic procedures unless medically necessary for correcting functional defects, 2) Experimental or investigational treatments, 3) Preexisting conditions during the 12-month waiting period, 4) Services not deemed medically necessary, and 5) Out-of-network services without prior authorization (except in emergencies)."
    
    # Emergency care questions
    elif "emergency" in question_lower:
        return "Emergency room visits have a $250 copayment, which is waived if you're admitted to the hospital. Ambulance services are covered at 80% after your deductible for medically necessary transportation."
    
    # Default response for other questions
    else:
        return f"Based on your {insurance_type} insurance policy, I would need more specific information to answer your question accurately. Could you please provide more details or ask a more specific question about your coverage, deductibles, copayments, or exclusions?"

def identify_question_type(question: str) -> str:
    """
    Identify the type of question being asked to provide a more tailored response
    """
    question_lower = question.lower()
    
    # Check for personal recommendation questions
    if any(phrase in question_lower for phrase in ["should i", "better for me", "recommend", "best for my", "good for my situation"]):
        return "recommendation"
    
    # Check for coverage questions
    elif any(phrase in question_lower for phrase in ["cover", "covered", "coverage", "pay for", "reimburse"]):
        return "coverage"
    
    # Check for policy comparisons
    elif any(phrase in question_lower for phrase in ["compare", "difference", "better", "versus", "vs"]):
        return "comparison"
    
    # Check for definition/explanation questions
    elif any(phrase in question_lower for phrase in ["what is", "what does", "mean", "define", "explain"]):
        return "definition"
    
    # Default to general interpretation
    return "general"

def extract_personal_context(question: str) -> Dict[str, Any]:
    """
    Extract personal context from the user's question to provide more tailored responses
    """
    context = {}
    
    # Simple extraction of age
    age_match = re.search(r'I am (\d+)', question) or re.search(r'(\d+) years old', question)
    if age_match:
        context["age"] = int(age_match.group(1))
    
    # Simple extraction of family status
    if re.search(r'married|spouse|wife|husband', question, re.IGNORECASE):
        context["married"] = True
    
    if re.search(r'kids|children|child|baby|infant', question, re.IGNORECASE):
        context["has_children"] = True
    
    # Health conditions
    if re.search(r'chronic|condition|diabetes|asthma|heart|cancer', question, re.IGNORECASE):
        context["has_health_conditions"] = True
    
    return context

def get_related_terms(question: str, identified_terms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Find terms in the identified terms list that are related to the user's question
    """
    related_terms = []
    
    # Lowercase the question for case-insensitive matching
    question_lower = question.lower()
    
    for term_info in identified_terms:
        # If the term appears in the question, consider it related
        if term_info["term"].lower() in question_lower:
            related_terms.append(term_info)
    
    return related_terms
