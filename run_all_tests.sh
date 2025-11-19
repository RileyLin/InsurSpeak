#!/bin/bash
# Script to run all tests (backend + frontend)

set -e  # Exit on error

echo "=================================="
echo "🧪 InsurSpeak Test Runner"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Backend tests
echo "${YELLOW}📦 Running Backend Tests...${NC}"
cd backend

if pytest --cov=. --cov-report=term-missing -v; then
    echo "${GREEN}✅ Backend tests passed!${NC}"
else
    echo "${RED}❌ Backend tests failed!${NC}"
    exit 1
fi

echo ""
cd ..

# Frontend tests
echo "${YELLOW}⚛️  Running Frontend Tests...${NC}"
cd frontend

if npm test -- --coverage --watchAll=false; then
    echo "${GREEN}✅ Frontend tests passed!${NC}"
else
    echo "${RED}❌ Frontend tests failed!${NC}"
    exit 1
fi

echo ""
cd ..

# Summary
echo "=================================="
echo "${GREEN}✅ All Tests Passed!${NC}"
echo "=================================="
echo ""
echo "Coverage reports generated:"
echo "  Backend:  backend/htmlcov/index.html"
echo "  Frontend: frontend/coverage/lcov-report/index.html"
echo ""
echo "🚀 Ready to commit and push!"
