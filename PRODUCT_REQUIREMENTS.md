# InsurSpeak - Product Requirements & Phased Development Plan

## Vision Statement

InsurSpeak is a simple, powerful tool that helps people understand their insurance policies and maximize their benefits. Users can upload their insurance documents, get AI-powered summaries of their rights and coverage, and receive personalized recommendations for claims they can file based on their life situations.

---

## Current State Analysis

### ✅ What's Already Built (MVP v0.1)
- **Tech Stack**: FastAPI backend + React frontend with Material-UI
- **Document Processing**: Upload PDFs, extract text, identify insurance terms
- **Term Explanation**: 30+ common insurance terms with plain-language explanations
- **Q&A System**: Ask natural language questions about policies using OpenAI GPT-4o
- **Basic UI**: Homepage, document upload page, Q&A interface
- **No Database**: All processing is in-memory (no persistence)
- **No User Accounts**: Single-session usage only

### ❌ What's Missing Based on Your Vision
1. **Homepage Content**: No links or explanations for popular insurance types and rights
2. **Policy Summarization**: Terms are identified but not organized into actionable summaries
3. **Rights & Benefits Organization**: No structured view of "what can I claim" vs "what I cannot"
4. **User Profiles**: No account system or saved policies
5. **Situation-Based Claims**: No "I describe my situation → get claim recommendations" feature
6. **Policy Matching**: No matching policies to personal life status
7. **Multi-Policy Management**: Can't compare/aggregate multiple insurance policies

---

## Detailed Requirements by Phase

## PHASE 1: Enhanced Core Functionality (MVP v1.0)
**Goal**: Make the PDF upload → summarize → understand rights workflow really solid

### 1.1 Enhanced Homepage
**User Story**: As a visitor, I want to understand what insurance rights I have for common insurance types before uploading my documents.

**Requirements**:
- [ ] **Popular Insurance Types Section**
  - Display cards for: Health, Auto, Life, Disability, Travel, Homeowners/Renters
  - Each card shows: icon, brief description, 3-5 key rights/benefits people have
  - "Learn More" expands to show detailed rights information
  - Examples:
    - Health: "Right to appeal denials", "Preventive care coverage", "Emergency care rights"
    - Travel: "Flight delay compensation", "Trip cancellation rights", "Lost baggage claims"
    - Auto: "Accident claim process", "Rental car coverage", "Glass/windshield repair"

- [ ] **How It Works - Updated**
  - Step 1: Upload your insurance policy PDF
  - Step 2: Get AI-powered summary of your coverage, rights, and benefits
  - Step 3: Understand what you can claim and what's excluded
  - Step 4: [Future] Describe your situation and get claim recommendations

- [ ] **Educational Resources**
  - Link to common insurance terminology guide
  - Link to "How to file a claim" general guidance
  - Insurance rights by state/country (basic info)

### 1.2 Smart Policy Summarization
**User Story**: As a user who uploaded my policy, I want a clear, organized summary of what I'm covered for, what I can claim, and what's excluded.

**Requirements**:
- [ ] **Structured Summary Dashboard** (new page after document processing)

  **A. Coverage Overview Card**
  - Insurance type (Health/Life/Auto/Travel/etc.)
  - Policy holder name (extracted if possible)
  - Policy number (extracted if possible)
  - Coverage period/dates
  - Key coverage limits (max amounts)

  **B. Benefits & Rights Section**
  - Organized list of what IS covered
  - Categorized by type (e.g., Medical: Doctor visits, Prescriptions, Emergency care)
  - Each item shows: benefit name, coverage amount/percentage, limitations
  - Highlight "Key Benefits You Should Know About"

  **C. Exclusions & Limitations Section**
  - Clear list of what is NOT covered
  - Common scenarios that are excluded
  - Waiting periods or conditions
  - Highlight in red/warning color

  **D. Claims Process Section**
  - How to file a claim (extracted from policy)
  - Required documentation
  - Timelines (when to file by)
  - Contact information for claims

  **E. Deductibles & Out-of-Pocket Costs**
  - Deductible amounts
  - Co-pays and co-insurance
  - Out-of-pocket maximums
  - Premium information if available

  **F. Special Rights & Protections**
  - Appeal rights
  - Grace periods
  - Renewal rights
  - Special provisions

- [ ] **AI-Powered Insights**
  - "Hidden Benefits You Might Miss" - AI identifies less obvious coverage
  - "Watch Out For" - AI highlights important exclusions or limitations
  - "Money-Saving Tips" - How to maximize benefits

- [ ] **Export & Share**
  - Download summary as PDF
  - Share link (requires implementing basic document storage)
  - Print-friendly view

### 1.3 Enhanced Document Processing
**Requirements**:
- [ ] **Multi-Format Support**
  - Support PDF, DOCX, DOC, TXT, images (with OCR)
  - Better error handling for scanned/image PDFs
  - Implement OCR using Tesseract or cloud OCR service

- [ ] **Better Parsing & Extraction**
  - Improved section detection (Coverage, Exclusions, Claims Process, Definitions)
  - Extract structured data: policy numbers, dates, amounts, percentages
  - Table extraction from PDFs (often coverage limits are in tables)
  - Named entity recognition for key terms

- [ ] **Insurance Type Detection**
  - Auto-detect insurance type from document content
  - Support 6+ insurance types: Health, Auto, Life, Disability, Travel, Home/Renters, Pet
  - Custom terminology per insurance type

### 1.4 Improved Q&A System
**Requirements**:
- [ ] **Contextual Understanding**
  - Remember previous questions in the session
  - Reference specific sections when answering
  - Cite page numbers or sections from the policy

- [ ] **Suggested Questions**
  - Auto-generate relevant questions based on the policy
  - "You might want to ask..." suggestions
  - Common questions for this insurance type

- [ ] **Answer Quality**
  - Always cite source section from policy
  - Confidence score on answers
  - "I'm not sure, but here's what I found..." for unclear cases

---

## PHASE 2: User Accounts & Policy Management
**Goal**: Allow users to save policies, create profiles, and manage multiple insurance documents

### 2.1 User Authentication & Profiles
**Requirements**:
- [ ] **Account System**
  - Email/password registration and login
  - OAuth options (Google, Apple)
  - Email verification
  - Password reset flow

- [ ] **User Profile**
  - Basic info: name, date of birth, location
  - Family information: marital status, dependents
  - Health information: pre-existing conditions (optional, for better recommendations)
  - Lifestyle: travel frequency, vehicle ownership, home ownership
  - Occupation and employment status

### 2.2 Policy Library
**Requirements**:
- [ ] **Document Storage**
  - Upload and save multiple insurance policies
  - Organize by insurance type
  - Tag policies (active, expired, archived)
  - Search through saved policies

- [ ] **Policy Dashboard**
  - View all policies at a glance
  - Quick stats: total coverage value, number of active policies
  - Expiration reminders
  - Coverage gaps identification (e.g., "You have health but no disability insurance")

- [ ] **Database Implementation**
  - MongoDB for document storage
  - Collections: users, policies, conversations, claims_history
  - Secure file storage (AWS S3, Google Cloud Storage, or local encrypted)

---

## PHASE 3: Situation-Based Claim Recommendations (The Core Vision!)
**Goal**: "Something happened to me → Tell me what I can claim"

### 3.1 Situation Input & Analysis
**User Story**: As a user, I want to describe what happened to me and get recommendations for claims I can file across all my insurance policies.

**Requirements**:
- [ ] **Situation Description Interface**
  - Free-form text input: "My flight was delayed 6 hours"
  - Structured form option with common scenarios:
    - Medical: Doctor visit, Prescription, Emergency, Surgery, Dental, Vision
    - Travel: Flight delay, Cancellation, Lost baggage, Medical emergency abroad
    - Auto: Accident, Theft, Glass damage, Roadside assistance
    - Home: Damage, Theft, Liability claim
    - Life events: Disability, Critical illness, Death of insured

  - Capture key details:
    - Date of incident
    - Location
    - Cost/impact
    - Supporting details

- [ ] **AI-Powered Policy Matching**
  - Analyze user's situation against ALL their policies
  - Identify applicable coverage across different policies
  - Match situation keywords to policy terms and coverage sections
  - Consider policy effective dates and user's timeline

- [ ] **Claim Recommendations**
  - List all potential claims user can file
  - Priority ranking (high value, easy to claim, likely approval)
  - For each claim show:
    - Which policy it applies to
    - Estimated coverage amount
    - What documentation is needed
    - How to file (step-by-step)
    - Timeline expectations
    - Likelihood of approval (based on policy terms)

- [ ] **Multi-Policy Coordination**
  - Identify when multiple policies might cover the same incident
  - Primary vs. secondary coverage coordination
  - Avoid duplicate claims
  - Maximize total reimbursement

### 3.2 Claim Assistant
**Requirements**:
- [ ] **Document Checklist**
  - Generate required documents list for each claim
  - Upload and attach supporting documents
  - Document validation (is this the right type of document?)

- [ ] **Claim Drafting**
  - Generate claim letter/form text
  - Fill in policy numbers, dates, amounts automatically
  - Export ready-to-submit claims

- [ ] **Claim Tracking** (Future)
  - Track submitted claims status
  - Reminders for follow-ups
  - History of past claims

### 3.3 Proactive Recommendations
**Requirements**:
- [ ] **Life Event Triggers**
  - User updates profile (e.g., gets married, has a baby)
  - System suggests: "Update your beneficiaries", "You may now qualify for dependent coverage"

- [ ] **Underutilized Benefits**
  - Analyze past behavior vs. available benefits
  - "You have $500 in unused dental benefits this year"
  - "Your gym membership might be covered - here's how to claim"

- [ ] **Preventive Reminders**
  - "Your annual physical is covered at 100% - schedule it before end of year"
  - "Renewal coming up - compare with other policies"

---

## PHASE 4: Advanced Features & Intelligence
**Goal**: Make InsurSpeak the smartest insurance assistant

### 4.1 Smart Insights & Analytics
**Requirements**:
- [ ] **Coverage Analysis**
  - Compare user's coverage to benchmarks
  - Identify gaps in coverage
  - Suggest additional insurance types to consider

- [ ] **Cost Optimization**
  - Analyze premiums vs. benefits utilized
  - Identify overlapping coverage (paying twice for same benefit)
  - Savings opportunities

- [ ] **Historical Trends**
  - Track claims filed over time
  - Reimbursement success rates
  - Most valuable benefits used

### 4.2 Collaborative Features
**Requirements**:
- [ ] **Family Accounts**
  - Link family members' policies
  - Dependent coverage management
  - Share access to specific policies

- [ ] **Advisor Sharing**
  - Share policies with insurance brokers/advisors
  - Collaboration on claim filing
  - Comments and notes on policies

### 4.3 Integration & Automation
**Requirements**:
- [ ] **Email Integration**
  - Forward policy documents via email to auto-import
  - Email claims directly from platform

- [ ] **Calendar Integration**
  - Add policy renewal dates
  - Claim deadline reminders

- [ ] **Insurance Company APIs**
  - Direct integration with major insurers for real-time policy data
  - Auto-import policy updates
  - Check claim status automatically

---

## Technical Architecture Considerations

### Database Schema (Phase 2+)

```
users
  - _id
  - email, password_hash
  - profile { name, dob, location, family_info, health_info, lifestyle }
  - created_at, updated_at

policies
  - _id
  - user_id
  - insurance_type
  - policy_number, provider_name
  - file_url, original_filename
  - processed_data {
      coverage_overview, benefits, exclusions,
      claims_process, costs, special_rights
    }
  - extracted_entities (structured data)
  - status (active, expired, archived)
  - effective_date, expiration_date
  - created_at, updated_at

situations (claims scenarios)
  - _id
  - user_id
  - description
  - incident_date, location
  - category (medical, travel, auto, etc.)
  - structured_details {}
  - recommendations [] (array of claim recommendations)
  - created_at

conversations
  - _id
  - user_id
  - policy_id (optional)
  - messages [] (Q&A history)
  - created_at

claims_history (future)
  - _id
  - user_id
  - policy_id
  - situation_id
  - claim_details
  - status, amount, outcome
  - filed_date, resolution_date
```

### AI/ML Enhancements

1. **Better NLP Models**
   - Fine-tune models on insurance documents
   - Custom named entity recognition for insurance terms
   - Sentence transformers for semantic search

2. **Embeddings & Semantic Search**
   - Create embeddings for policy sections
   - Semantic search for better Q&A
   - Match situations to coverage using embeddings

3. **RAG (Retrieval Augmented Generation)**
   - Use vector database (Pinecone, Weaviate, or Qdrant)
   - Store policy sections as vectors
   - Better context for AI answers

### Security & Compliance

1. **Data Protection**
   - Encrypt sensitive data at rest
   - HIPAA compliance considerations (health insurance)
   - User data deletion (GDPR right to be forgotten)

2. **Document Security**
   - Encrypted file storage
   - Access controls
   - Audit logs

---

## Success Metrics

### Phase 1 Metrics
- Document processing success rate > 95%
- Summary completeness score (did we extract all sections?)
- User satisfaction with summaries
- Time to understand policy (before/after)

### Phase 2 Metrics
- User registration and retention rates
- Average policies per user
- Return visit frequency

### Phase 3 Metrics (The Big Ones!)
- **Claim recommendation accuracy**: % of recommendations that user could actually file
- **Value unlocked**: Total $ amount claimed that users wouldn't have known about
- **Time saved**: Hours saved vs. manually reading policies
- **Claim success rate**: % of recommended claims that got approved

### Phase 4 Metrics
- Coverage gap identification accuracy
- Cost savings identified per user
- User engagement with proactive recommendations

---

## Development Priorities

### IMMEDIATE (Phase 1 - Weeks 1-4)
1. Enhanced homepage with insurance types and rights
2. Smart summarization dashboard
3. Improve PDF parsing and data extraction
4. Better Q&A with citations

### SHORT-TERM (Phase 2 - Weeks 5-10)
1. User authentication system
2. Database setup (MongoDB)
3. Policy library and management
4. Document persistence

### MEDIUM-TERM (Phase 3 - Weeks 11-20)
1. Situation input interface
2. AI policy matching algorithm
3. Claim recommendations engine
4. Multi-policy coordination

### LONG-TERM (Phase 4 - Months 6+)
1. Advanced analytics
2. Integrations
3. Collaborative features
4. Mobile app

---

## Open Questions & Decisions Needed

1. **Geography**: Will this be US-focused or international? (Different insurance regulations)
2. **Insurance Types**: Which insurance types to prioritize beyond health, auto, life?
3. **Monetization**: Free tool, freemium, subscription? This affects feature prioritization
4. **AI Costs**: OpenAI API costs can add up - consider cost optimization strategies
5. **OCR Provider**: Tesseract (free, local) vs. cloud OCR (Google/AWS - paid but better)?
6. **Hosting**: Where to deploy? (AWS, Google Cloud, Vercel, etc.)
7. **Legal**: Will you need terms of service, disclaimers, legal review?

---

## Next Steps

Please review this document and let me know:
1. Does this capture your vision accurately?
2. Any requirements missing or misunderstood?
3. Which phase should we start with? (I recommend Phase 1)
4. Any changes to priorities or scope?
5. Answers to the open questions above?

Once approved, I'll create detailed technical tasks and begin implementation!
