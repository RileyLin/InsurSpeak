# InsurSpeak Setup Guide

This guide will walk you through setting up and running the InsurSpeak application locally.

## Prerequisites

- Python 3.8+ for the backend
- Node.js 14+ and npm for the frontend
- OpenAI API key for LLM functionality

## Backend Setup

1. Navigate to the backend directory:
   ```
   cd insurspeak/backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install dependencies:
   ```
   pip install -r ../requirements.txt
   ```

5. Create a `.env` file based on `.env.example`:
   ```
   cp .env.example .env
   ```

6. Edit the `.env` file and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

7. Start the backend server:
   ```
   uvicorn main:app --reload
   ```

The API will be available at http://localhost:8000

## Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd insurspeak/frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

The application will be available at http://localhost:3000

## Using the Application

1. Upload or paste an insurance document on the "Process Document" page
2. Select the type of insurance (health, life, or disability)
3. Click "Process Document" to analyze the content
4. Navigate to the "Ask Questions" page to interact with the document
5. Type your questions about the insurance policy to receive simple, easy-to-understand explanations

## Features

- Document upload and processing
- Insurance jargon identification and explanation
- Natural language question answering
- Personalized recommendations based on your situation
- Support for health, life, and disability insurance documents

## Troubleshooting

- If the backend fails to start, ensure you have provided a valid OpenAI API key
- If document processing is slow, try reducing the document size or pasting only relevant sections
- For any issues with term highlighting, try refreshing the page after document processing
