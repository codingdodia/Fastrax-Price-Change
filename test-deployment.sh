#!/bin/bash

echo "Testing local deployment setup..."

# Check if frontend builds successfully
echo "Building frontend..."
cd frontend
npm install
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Frontend build successful"
else
    echo "❌ Frontend build failed"
    exit 1
fi

cd ..

# Check if backend requirements are satisfied
echo "Checking backend requirements..."
cd backend/src
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Backend requirements satisfied"
else
    echo "❌ Backend requirements failed"
    exit 1
fi

echo "✅ All checks passed! Ready for Vercel deployment."
echo ""
echo "Next steps:"
echo "1. Commit and push to GitHub"
echo "2. Connect repository to Vercel"
echo "3. Deploy!"