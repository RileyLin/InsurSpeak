import os
from typing import List, Dict, Any
import openai
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Dictionary of pre-defined explanations for common terms
# In a production app, this would be stored in a database
COMMON_EXPLANATIONS = {
    "premium": "The amount of money you pay to your insurance company for coverage. This can be paid monthly, quarterly, or annually.",
    
    "deductible": "The amount you must pay out of pocket for covered services before your insurance starts paying. For example, if your deductible is $1,000, you'll pay the first $1,000 of covered services yourself.",
    
    "copay": "A fixed amount you pay each time you receive a covered service. For example, a $30 copay for a doctor visit means you pay $30 regardless of the actual cost of the visit.",
    
    "coinsurance": "The percentage of costs you pay for a covered service after you've met your deductible. For example, if you have 20% coinsurance, you pay 20% of the cost and your insurance pays 80%.",
    
    "out-of-pocket maximum": "The most you'll have to pay for covered services in a policy period (usually one year). After you reach this amount, your insurance will pay 100% of the costs for covered services.",
    
    "beneficiary": "The person(s) or entity you choose to receive the benefits (like a payout) from your insurance policy, often after your death in life insurance policies.",
    
    "policyholder": "The person who owns the insurance policy. They are responsible for paying premiums and are typically the one covered by the insurance.",
    
    "preexisting condition": "A health condition you had before your insurance coverage started. Some policies limit or exclude coverage for these conditions.",
    
    "waiting period": "The time you must wait after purchasing a policy before certain benefits become available or before you can file certain types of claims.",
    
    "rider": "An optional addition to your insurance policy that provides additional benefits or coverage for an extra cost."
}

def generate_explanations(identified_terms: List[Dict[str, Any]], insurance_type: str) -> List[Dict[str, Any]]:
    """
    Generate plain language explanations for identified terms
    """
    terms_with_explanations = []
    
    for term_info in identified_terms:
        term = term_info["term"].lower()
        
        # Check if we have a pre-defined explanation
        if term in COMMON_EXPLANATIONS:
            explanation = COMMON_EXPLANATIONS[term]
            implications = get_implications(term, insurance_type)
            
            terms_with_explanations.append({
                **term_info,
                "explanation": explanation,
                "implications": implications,
                "source": "database"
            })
        else:
            # Generate explanation using LLM
            try:
                llm_response = generate_llm_explanation(term_info, insurance_type)
                
                terms_with_explanations.append({
                    **term_info,
                    "explanation": llm_response["explanation"],
                    "implications": llm_response["implications"],
                    "source": "llm"
                })
            except Exception as e:
                print(f"Error generating explanation for {term}: {e}")
                # Fallback to a generic explanation
                terms_with_explanations.append({
                    **term_info,
                    "explanation": f"This is insurance terminology related to {term_info['category']}.",
                    "implications": "You may want to ask your insurance provider for clarification.",
                    "source": "fallback"
                })
    
    return terms_with_explanations

def generate_llm_explanation(term_info: Dict[str, Any], insurance_type: str) -> Dict[str, str]:
    """
    Generate an explanation for a term using OpenAI's API
    """
    # Format the prompt with the term and its context
    prompt = f"""
    You are an expert insurance translator helping people understand complex insurance terms.
    
    Please explain the following insurance term in simple language (8th-grade reading level):
    
    Term: {term_info['term']}
    Context: {term_info['context']}
    Insurance Type: {insurance_type}
    Category: {term_info['category']}
    
    Provide:
    1. A clear, simple explanation of what this term means
    2. Any practical implications this might have for the policyholder
    
    Format your response as a JSON object with the following structure:
    {{
      "explanation": "your simple explanation here",
      "implications": "practical implications for the policyholder"
    }}
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",  # Use appropriate model
            messages=[
                {"role": "system", "content": "You are an insurance expert that explains complex terms in simple language."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        
        # Parse the response
        content = response.choices[0].message.content
        
        # Extract the JSON part
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = content[json_start:json_end]
            return json.loads(json_str)
        else:
            # If JSON parsing fails, create a structured response
            return {
                "explanation": content[:150] if len(content) > 150 else content,
                "implications": "Please consult your insurance provider for specific details about how this affects your policy."
            }
            
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return {
            "explanation": f"This term ({term_info['term']}) is related to {insurance_type} insurance.",
            "implications": "Please consult your insurance provider for specific details."
        }

def get_implications(term: str, insurance_type: str) -> str:
    """
    Get implications for common terms based on insurance type
    """
    implications_map = {
        "premium": {
            "health": "If you miss premium payments, your health coverage could be terminated.",
            "life": "If you miss premium payments, your life insurance policy could lapse and you might lose coverage.",
            "disability": "If you miss premium payments, your disability protection could end when you need it most."
        },
        "deductible": {
            "health": "You'll need to budget for this amount before your insurance helps with costs.",
            "life": "Life insurance typically doesn't have deductibles.",
            "disability": "This is the amount of time (elimination period) or money you must wait/spend before benefits begin."
        },
        "waiting period": {
            "health": "You won't be covered for certain services during this time, so plan accordingly.",
            "life": "If death occurs during this period, the full benefit may not be paid.",
            "disability": "You won't receive benefits during this period, so have emergency savings ready."
        }
    }
    
    # Get the specific implication for this term and insurance type
    if term in implications_map and insurance_type.lower() in implications_map[term]:
        return implications_map[term][insurance_type.lower()]
    
    # Default generic implications
    return "This may affect your coverage or costs. Check your specific policy details."
