#!/bin/bash

# Move to frontend directory and build
cd frontend
npm ci
npm run build

# Move build output to root
cd ..
mv frontend/dist .

echo "Build completed successfully"