# InsurSpeak Deployment Comparison Guide

## Executive Summary

This guide compares three deployment strategies for InsurSpeak, analyzing cost, complexity, scalability, and maintenance requirements.

| Criteria | AWS Native | Railway + Vercel + MongoDB | Supabase + Vercel |
|----------|-----------|---------------------------|-------------------|
| **Initial Cost** | $50-100/mo | $20-40/mo | $25-45/mo |
| **Complexity** | High | Low | Very Low |
| **Setup Time** | 4-8 hours | 1-2 hours | 30-60 minutes |
| **Scalability** | Excellent | Good | Good |
| **Vendor Lock-in** | High (AWS) | Low (portable) | Medium (Supabase) |
| **Best For** | Enterprise, high scale | Startups, MVPs | Rapid prototyping |

---

## Path 1: AWS Native Stack

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      AWS Cloud                               │
│                                                              │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │ CloudFront   │─────▶│   S3 Bucket  │ (React Frontend)   │
│  │   (CDN)      │      │              │                    │
│  └──────────────┘      └──────────────┘                    │
│         │                                                    │
│         │                                                    │
│  ┌──────▼──────────────────────────────────────┐           │
│  │         Application Load Balancer            │           │
│  └──────┬──────────────────────────────────────┘           │
│         │                                                    │
│  ┌──────▼──────────┐      ┌──────────────┐                │
│  │  ECS Fargate    │─────▶│  DocumentDB  │ (MongoDB compat)│
│  │  (FastAPI)      │      │  or          │                │
│  │                 │      │  DynamoDB    │                │
│  └─────────────────┘      └──────────────┘                │
│         │                                                    │
│  ┌──────▼──────────┐                                       │
│  │   S3 Bucket     │ (PDF Storage)                         │
│  └─────────────────┘                                       │
└─────────────────────────────────────────────────────────────┘
```

### Services Used

1. **Frontend:** S3 + CloudFront
2. **Backend:** ECS Fargate or Lambda
3. **Database:** DocumentDB (MongoDB compatible) or DynamoDB
4. **Storage:** S3 for PDF files
5. **Auth:** Cognito (optional, or keep JWT)
6. **Networking:** VPC, ALB, Route53

### Step-by-Step Deployment

#### Prerequisites
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS CLI
aws configure
# Enter: Access Key ID, Secret Access Key, Region (us-east-1), Output (json)

# Install Docker
sudo apt-get update
sudo apt-get install docker.io
```

#### Step 1: Database Setup (DocumentDB)

```bash
# Create DocumentDB cluster (MongoDB compatible)
aws docdb create-db-cluster \
    --db-cluster-identifier insurspeak-cluster \
    --engine docdb \
    --master-username admin \
    --master-user-password YourSecurePassword123! \
    --vpc-security-group-ids sg-xxxxxxxxx \
    --db-subnet-group-name default

# Create instance
aws docdb create-db-instance \
    --db-instance-identifier insurspeak-instance \
    --db-instance-class db.t3.medium \
    --engine docdb \
    --db-cluster-identifier insurspeak-cluster

# Get connection string
aws docdb describe-db-clusters \
    --db-cluster-identifier insurspeak-cluster \
    --query 'DBClusters[0].Endpoint' \
    --output text
# Result: insurspeak-cluster.cluster-xxxxx.us-east-1.docdb.amazonaws.com
```

**Connection String:**
```
mongodb://admin:YourSecurePassword123!@insurspeak-cluster.cluster-xxxxx.us-east-1.docdb.amazonaws.com:27017/?tls=true&tlsCAFile=rds-combined-ca-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false
```

#### Step 2: Backend Deployment (ECS Fargate)

**Create Dockerfile** (already exists, verify):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and push to ECR:**
```bash
# Create ECR repository
aws ecr create-repository --repository-name insurspeak-backend

# Get ECR login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and tag
cd backend
docker build -t insurspeak-backend .
docker tag insurspeak-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/insurspeak-backend:latest

# Push
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/insurspeak-backend:latest
```

**Create ECS Task Definition** (`ecs-task-definition.json`):
```json
{
  "family": "insurspeak-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "insurspeak-backend",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/insurspeak-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "MONGODB_URL", "value": "mongodb://admin:...@insurspeak-cluster..."},
        {"name": "OPENAI_API_KEY", "value": "sk-..."},
        {"name": "SECRET_KEY", "value": "your-secret-key"},
        {"name": "CORS_ORIGINS", "value": "https://insurspeak.com"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/insurspeak-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

**Deploy to ECS:**
```bash
# Create cluster
aws ecs create-cluster --cluster-name insurspeak-cluster

# Register task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create ALB (Application Load Balancer) - use AWS Console or CLI
# Then create ECS service
aws ecs create-service \
    --cluster insurspeak-cluster \
    --service-name insurspeak-backend-service \
    --task-definition insurspeak-backend \
    --desired-count 2 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=insurspeak-backend,containerPort=8000"
```

#### Step 3: Frontend Deployment (S3 + CloudFront)

```bash
# Build frontend
cd frontend
npm install
REACT_APP_API_URL=https://api.insurspeak.com npm run build

# Create S3 bucket
aws s3 mb s3://insurspeak-frontend --region us-east-1

# Configure as static website
aws s3 website s3://insurspeak-frontend --index-document index.html --error-document index.html

# Upload build
aws s3 sync build/ s3://insurspeak-frontend --acl public-read

# Create CloudFront distribution
aws cloudfront create-distribution \
    --origin-domain-name insurspeak-frontend.s3.amazonaws.com \
    --default-root-object index.html
```

**CloudFront Configuration (JSON):**
```json
{
  "Origins": {
    "Items": [
      {
        "Id": "S3-insurspeak-frontend",
        "DomainName": "insurspeak-frontend.s3.amazonaws.com",
        "S3OriginConfig": {
          "OriginAccessIdentity": ""
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-insurspeak-frontend",
    "ViewerProtocolPolicy": "redirect-to-https",
    "Compress": true
  },
  "CustomErrorResponses": {
    "Items": [
      {
        "ErrorCode": 404,
        "ResponsePagePath": "/index.html",
        "ResponseCode": "200"
      }
    ]
  }
}
```

#### Step 4: Domain & SSL

```bash
# Request certificate in ACM
aws acm request-certificate \
    --domain-name insurspeak.com \
    --subject-alternative-names *.insurspeak.com \
    --validation-method DNS

# Create Route53 hosted zone
aws route53 create-hosted-zone --name insurspeak.com --caller-reference $(date +%s)

# Add DNS records (use AWS Console for easier setup)
# Point insurspeak.com -> CloudFront distribution
# Point api.insurspeak.com -> ALB
```

### AWS Cost Breakdown

| Service | Tier | Monthly Cost |
|---------|------|--------------|
| DocumentDB (t3.medium) | 1 instance | ~$75 |
| ECS Fargate (0.5 vCPU, 1GB) | 2 tasks | ~$35 |
| S3 (frontend + PDFs) | 10GB | ~$0.23 |
| CloudFront | 100GB transfer | ~$8.50 |
| ALB | Standard | ~$16 |
| Route53 | 1 hosted zone | ~$0.50 |
| **Total (Month 1)** | | **~$135** |

**Cost Optimization:**
- Use DynamoDB instead of DocumentDB: Save ~$60/mo (but requires code changes)
- Use Lambda instead of Fargate: Save ~$25/mo (for low traffic)
- Reserved instances: Save 30-50% after 1 year

---

## Path 2: Railway + Vercel + MongoDB Atlas (Original)

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Vercel CDN                               │
│                   (React Frontend)                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ API Calls
                 │
┌────────────────▼────────────────────────────────────────────┐
│                   Railway                                    │
│              (FastAPI Backend)                               │
│                                                              │
│  ┌─────────────────────┐      ┌──────────────────────┐     │
│  │  Python Container   │─────▶│  MongoDB Atlas       │     │
│  │  (Auto-deployed)    │      │  (Managed Database)  │     │
│  └─────────────────────┘      └──────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Services Used

1. **Frontend:** Vercel (auto-deploy from Git)
2. **Backend:** Railway (containerized FastAPI)
3. **Database:** MongoDB Atlas (M0 free tier → M10)
4. **Storage:** MongoDB GridFS or Railway volumes

### Step-by-Step Deployment

#### Step 1: MongoDB Atlas Setup

```bash
# 1. Go to https://www.mongodb.com/cloud/atlas
# 2. Create free account
# 3. Create new cluster (M0 Free tier for testing, M10+ for production)
# 4. Setup database user and network access

# Click "Create Database" → "Build a Cluster"
# Choose: AWS, us-east-1, M10 (or M0 Free)
# Cluster name: insurspeak-cluster

# Database Access → Add New Database User
# Username: insurspeak_admin
# Password: (generate secure password)
# Role: Atlas admin

# Network Access → Add IP Address
# Choose: "Allow access from anywhere" (0.0.0.0/0) for now
# Or add Railway's IP addresses

# Get connection string:
# Click "Connect" → "Connect your application"
# Copy: mongodb+srv://insurspeak_admin:<password>@insurspeak-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

**Replace in backend/.env:**
```env
MONGODB_URL=mongodb+srv://insurspeak_admin:YourPassword@insurspeak-cluster.xxxxx.mongodb.net/insurspeak?retryWrites=true&w=majority
```

#### Step 2: Railway Backend Deployment

**Method A: Using Railway CLI**

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
cd backend
railway init

# Set environment variables
railway variables set MONGODB_URL="mongodb+srv://..."
railway variables set OPENAI_API_KEY="sk-..."
railway variables set SECRET_KEY="your-secret-key-change-this"
railway variables set CORS_ORIGINS="https://your-app.vercel.app"

# Deploy
railway up

# Get URL
railway domain
# Example: insurspeak-backend-production.up.railway.app
```

**Method B: Using Railway Dashboard (Easier)**

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect GitHub account and select InsurSpeak repository
4. Railway auto-detects Python/FastAPI
5. Set root directory: `/backend`
6. Add environment variables:
   ```
   MONGODB_URL=mongodb+srv://...
   OPENAI_API_KEY=sk-...
   SECRET_KEY=your-secret-key
   CORS_ORIGINS=https://your-app.vercel.app
   ```
7. Click "Deploy" - Railway auto-builds and deploys
8. Generate domain: Settings → Generate Domain
   - Result: `insurspeak-backend.up.railway.app`

**Create `railway.json`** (optional, for custom config):
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300
  }
}
```

#### Step 3: Vercel Frontend Deployment

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
cd frontend
vercel

# Follow prompts:
# - Link to existing project? No
# - Project name: insurspeak-frontend
# - Directory: ./
# - Build command: npm run build
# - Output directory: build

# Set environment variables
vercel env add REACT_APP_API_URL
# Enter: https://insurspeak-backend.up.railway.app

# Deploy to production
vercel --prod
```

**Method B: Vercel Dashboard (Easier)**

1. Go to https://vercel.com
2. Click "New Project" → Import from GitHub
3. Select InsurSpeak repository
4. Configure:
   - Framework Preset: Create React App
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `build`
   - Environment Variables:
     ```
     REACT_APP_API_URL=https://insurspeak-backend.up.railway.app
     ```
5. Click "Deploy"
6. Custom domain: Settings → Domains → Add `insurspeak.com`

**Create `vercel.json`** (for SPA routing):
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ]
}
```

#### Step 4: Update CORS in Backend

```python
# backend/main.py
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,  # ["https://insurspeak.vercel.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Railway + Vercel Cost Breakdown

| Service | Tier | Monthly Cost |
|---------|------|--------------|
| MongoDB Atlas M10 | 2GB RAM, 10GB storage | $9 (with discounts) |
| Railway | 8GB RAM, unlimited requests | $20 |
| Vercel | Pro plan (custom domains) | $20 |
| **Total (Month 1)** | | **~$49** |

**Free Tier Option (for testing):**
- MongoDB Atlas M0: Free (512MB, limited connections)
- Railway Hobby: $5/mo (500 hours)
- Vercel Hobby: Free (no custom domains)
- **Total:** ~$5/mo

---

## Path 3: Supabase + Vercel

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Vercel CDN                               │
│                   (React Frontend)                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ API Calls (Direct to Supabase)
                 │
┌────────────────▼────────────────────────────────────────────┐
│                   Supabase                                   │
│                                                              │
│  ┌─────────────────────┐      ┌──────────────────────┐     │
│  │  PostgreSQL DB      │      │  Supabase Auth       │     │
│  │                     │      │  (Built-in)          │     │
│  └─────────────────────┘      └──────────────────────┘     │
│                                                              │
│  ┌─────────────────────┐      ┌──────────────────────┐     │
│  │  Edge Functions     │      │  Storage Buckets     │     │
│  │  (Deno/TypeScript)  │      │  (for PDFs)          │     │
│  └─────────────────────┘      └──────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Major Architecture Change Required

**NOTE:** Supabase uses PostgreSQL, not MongoDB. This requires significant code changes:

1. **Database Schema Migration:** Convert MongoDB collections to PostgreSQL tables
2. **Replace FastAPI Backend:** Use Supabase Edge Functions (Deno/TypeScript) or keep FastAPI with PostgreSQL
3. **Authentication:** Use Supabase Auth instead of JWT
4. **Storage:** Use Supabase Storage instead of GridFS

### Option A: Supabase with Edge Functions (Serverless)

#### Step 1: Supabase Project Setup

```bash
# 1. Go to https://supabase.com
# 2. Create new project
# 3. Get API keys from Settings → API

# Install Supabase CLI
npm install -g supabase

# Login
supabase login

# Link to project
supabase link --project-ref your-project-ref

# Initialize
supabase init
```

#### Step 2: Database Schema (PostgreSQL)

**Create tables in Supabase SQL Editor:**

```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  policy_count INTEGER DEFAULT 0,
  subscription_tier TEXT DEFAULT 'free'
);

-- Policies table
CREATE TABLE policies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  insurance_type TEXT NOT NULL,
  policy_name TEXT,
  document_text TEXT,
  summary JSONB,
  entities JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  status TEXT DEFAULT 'active'
);

-- Claims analyses table
CREATE TABLE claims_analyses (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  situation TEXT NOT NULL,
  recommendations JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE claims_analyses ENABLE ROW LEVEL SECURITY;

-- Policies: Users can only see their own
CREATE POLICY "Users can view own policies" ON policies
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own policies" ON policies
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own policies" ON policies
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own policies" ON policies
  FOR DELETE USING (auth.uid() = user_id);
```

#### Step 3: Edge Functions (Replace FastAPI)

**Create Edge Function for PDF Processing:**

```bash
# Create new edge function
supabase functions new process-document
```

**`supabase/functions/process-document/index.ts`:**

```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? ''
    )

    // Get authenticated user
    const authHeader = req.headers.get('Authorization')!
    const token = authHeader.replace('Bearer ', '')
    const { data: { user } } = await supabase.auth.getUser(token)

    if (!user) throw new Error('Not authenticated')

    // Parse form data
    const formData = await req.formData()
    const file = formData.get('file') as File
    const insuranceType = formData.get('insurance_type') as string

    // Extract text from PDF (use external library or API)
    const text = await extractPdfText(file)

    // Call OpenAI for summary
    const summary = await generateSummary(text, insuranceType)

    // Save to database
    const { data: policy, error } = await supabase
      .from('policies')
      .insert({
        user_id: user.id,
        insurance_type: insuranceType,
        document_text: text,
        summary: summary
      })
      .select()
      .single()

    if (error) throw error

    return new Response(
      JSON.stringify({ success: true, policy }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})

async function extractPdfText(file: File): Promise<string> {
  // Option 1: Use pdf-parse library (if available in Deno)
  // Option 2: Call external API (e.g., PyPDF2 microservice)
  // Option 3: Use AWS Textract

  // For now, placeholder:
  return "Extracted text..."
}

async function generateSummary(text: string, type: string): Promise<any> {
  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${Deno.env.get('OPENAI_API_KEY')}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'gpt-4o',
      messages: [
        { role: 'system', content: 'You are an insurance analyst...' },
        { role: 'user', content: `Analyze this ${type} policy: ${text}` }
      ],
      temperature: 0.3,
    })
  })

  const data = await response.json()
  return JSON.parse(data.choices[0].message.content)
}
```

**Deploy Edge Function:**

```bash
supabase functions deploy process-document --no-verify-jwt
```

#### Step 4: Frontend with Supabase Client

**Install Supabase client:**

```bash
cd frontend
npm install @supabase/supabase-js
```

**Create Supabase client (`frontend/src/supabaseClient.js`):**

```javascript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

**Update authentication:**

```javascript
// Sign up
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'password123'
})

// Sign in
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'password123'
})

// Get session
const { data: { session } } = await supabase.auth.getSession()

// Call Edge Function
const { data, error } = await supabase.functions.invoke('process-document', {
  body: formData
})
```

#### Step 5: Deploy to Vercel

Same as Path 2, but with Supabase environment variables:

```env
REACT_APP_SUPABASE_URL=https://xxxxx.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGc...
```

### Option B: Keep FastAPI, Use Supabase as PostgreSQL

**Simpler migration:** Keep FastAPI backend, just swap MongoDB for PostgreSQL.

**Update `requirements.txt`:**

```txt
# Remove: pymongo
# Add:
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
alembic==1.13.0
```

**Create SQLAlchemy models (`backend/models.py`):**

```python
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    hashed_password = Column(String, nullable=False)
    policy_count = Column(Integer, default=0)
    subscription_tier = Column(String, default="free")

class Policy(Base):
    __tablename__ = "policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    insurance_type = Column(String, nullable=False)
    policy_name = Column(String)
    document_text = Column(String)
    summary = Column(JSON)
    entities = Column(JSON)
```

**Deploy FastAPI to Railway** (same as Path 2) with PostgreSQL connection:

```env
DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres
```

### Supabase Cost Breakdown

| Service | Tier | Monthly Cost |
|---------|------|--------------|
| Supabase Pro | 8GB DB, 250GB bandwidth | $25 |
| Vercel Pro | Custom domains | $20 |
| **Total** | | **~$45** |

**Free Tier (for testing):**
- Supabase Free: 500MB DB, 1GB bandwidth
- Vercel Hobby: Free
- **Total:** $0/mo (with limitations)

---

## Comparison Matrix

### Cost Comparison

| Scenario | AWS Native | Railway + Vercel | Supabase + Vercel |
|----------|-----------|------------------|-------------------|
| **Free Tier** | N/A (AWS free tier expires) | $5/mo | $0/mo |
| **Startup (<1K users)** | $135/mo | $49/mo | $45/mo |
| **Growth (1K-10K users)** | $200/mo | $99/mo | $95/mo |
| **Scale (10K+ users)** | $300-500/mo | $200/mo | $200/mo |
| **Enterprise (100K+ users)** | $1000+/mo (best value) | $500/mo (may hit limits) | $500/mo (may hit limits) |

### Feature Comparison

| Feature | AWS Native | Railway + Vercel | Supabase + Vercel |
|---------|-----------|------------------|-------------------|
| **Auto-scaling** | ✅ Excellent | ✅ Good | ✅ Good |
| **Global CDN** | ✅ CloudFront | ✅ Vercel Edge | ✅ Vercel Edge |
| **Database Backups** | ✅ Automatic | ✅ Manual (Atlas auto) | ✅ Automatic (daily) |
| **Monitoring** | ✅ CloudWatch | ⚠️ Basic | ✅ Built-in |
| **Custom Domains** | ✅ Route53 | ✅ Easy | ✅ Easy |
| **SSL Certificates** | ✅ ACM | ✅ Auto (Let's Encrypt) | ✅ Auto |
| **Rollback** | ✅ Full control | ✅ Git-based | ✅ Git-based |
| **Multi-region** | ✅ Yes | ⚠️ Limited | ⚠️ Limited |

### Complexity Comparison

| Task | AWS Native | Railway + Vercel | Supabase + Vercel |
|------|-----------|------------------|-------------------|
| **Initial Setup** | 4-8 hours | 1-2 hours | 30-60 mins |
| **Deploy Updates** | 30-60 mins | 5 mins (git push) | 5 mins (git push) |
| **Scale Up** | Medium effort | Easy | Easy |
| **Debugging** | Complex (logs scattered) | Easy (unified dashboard) | Easy (unified dashboard) |
| **Cost Control** | Complex (many services) | Simple | Simple |

### Development Experience

| Aspect | AWS Native | Railway + Vercel | Supabase + Vercel |
|--------|-----------|------------------|-------------------|
| **Local Development** | Complex (Docker Compose) | Easy | Easy |
| **CI/CD** | Manual setup (CodePipeline) | Auto (Git integration) | Auto (Git integration) |
| **Preview Deployments** | No (manual) | ✅ Yes (Vercel) | ✅ Yes (Vercel) |
| **Database Migrations** | Manual | Manual | Built-in (Supabase CLI) |
| **Logs & Metrics** | CloudWatch (complex) | Simple dashboard | Simple dashboard |

---

## Recommendation

### For MVP / Early Startup (0-1K users): **Railway + Vercel + MongoDB Atlas**

**Why:**
- ✅ Fastest time to market (1-2 hours setup)
- ✅ Lowest cost ($5-49/mo)
- ✅ No code changes needed (works with current FastAPI + MongoDB)
- ✅ Auto-deploy from Git (push to deploy)
- ✅ Easy to understand billing
- ✅ Great developer experience

**Perfect for:** Testing product-market fit, fundraising demos, beta testing

### For Growth Stage (1K-10K users): **Railway + Vercel + MongoDB Atlas**

**Why:**
- ✅ Still cost-effective ($50-100/mo)
- ✅ Good performance and scaling
- ✅ Focus on product, not infrastructure
- ✅ Easy to migrate to AWS later if needed

**When to migrate to AWS:** When you reach $10K-20K/mo revenue or need multi-region

### For Enterprise / High Scale (100K+ users): **AWS Native**

**Why:**
- ✅ Best performance and reliability
- ✅ Full control and customization
- ✅ Multi-region capabilities
- ✅ Advanced monitoring and security
- ✅ Cost-effective at scale (economics of scale)

---

## Quick Start Guides

### Option 1: Railway + Vercel (Recommended for You)

**Total Time: 1-2 hours**

```bash
# 1. MongoDB Atlas (10 mins)
# - Go to mongodb.com/cloud/atlas
# - Create M0 free cluster or M10 ($9/mo)
# - Get connection string
# - Add to .env: MONGODB_URL=mongodb+srv://...

# 2. Railway Backend (20 mins)
cd backend
railway login
railway init
railway variables set MONGODB_URL="..."
railway variables set OPENAI_API_KEY="..."
railway up
railway domain  # Get your API URL

# 3. Vercel Frontend (15 mins)
cd frontend
vercel login
vercel env add REACT_APP_API_URL  # Enter Railway URL
vercel --prod

# 4. Test (15 mins)
# - Visit your Vercel URL
# - Upload a policy
# - Check if it works

# DONE! 🎉
```

### Option 2: AWS Native (Advanced)

**Total Time: 4-8 hours**

```bash
# 1. Setup AWS CLI and Docker (30 mins)
# 2. Create DocumentDB cluster (45 mins)
# 3. Build and push to ECR (30 mins)
# 4. Deploy ECS Fargate (60 mins)
# 5. Setup ALB and networking (45 mins)
# 6. Deploy frontend to S3 + CloudFront (45 mins)
# 7. Setup Route53 and SSL (30 mins)
# 8. Testing (45 mins)
```

### Option 3: Supabase (Requires Code Changes)

**Total Time: 8-16 hours (includes migration)**

```bash
# 1. Create Supabase project (15 mins)
# 2. Migrate database schema (2-3 hours)
# 3. Convert FastAPI to use PostgreSQL (3-4 hours)
# 4. Deploy Edge Functions OR keep FastAPI (2-3 hours)
# 5. Update frontend to use Supabase Auth (2-3 hours)
# 6. Deploy to Vercel (15 mins)
# 7. Testing (1-2 hours)
```

---

## Migration Path

If you start with Railway + Vercel and later need to migrate to AWS:

1. **Phase 1 (Day 1):** Export MongoDB data
2. **Phase 2 (Day 2-3):** Setup AWS infrastructure
3. **Phase 3 (Day 4):** Deploy backend to ECS
4. **Phase 4 (Day 5):** Deploy frontend to S3/CloudFront
5. **Phase 5 (Day 6):** Import data to DocumentDB
6. **Phase 6 (Day 7):** Switch DNS, monitor, cleanup

**Migration is straightforward** because:
- Backend is containerized (Docker)
- Database is MongoDB in both cases
- Frontend is static build

---

## Final Recommendation for InsurSpeak

### Start with: **Railway + Vercel + MongoDB Atlas**

**Timeline:**
1. **Week 1:** Deploy MVP to Railway + Vercel
2. **Month 1-6:** Validate product-market fit
3. **Month 6-12:** Scale to 1K-10K users on Railway
4. **Year 2:** If revenue > $20K/mo and users > 50K, migrate to AWS

**This approach:**
- ✅ Minimizes upfront investment
- ✅ Fastest time to market
- ✅ Lets you focus on product, not infrastructure
- ✅ Easy migration path when you need it

**Save AWS for when you have:**
- Proven business model
- Steady revenue ($20K+/mo)
- Team member who can manage AWS
- Need for multi-region or advanced features
