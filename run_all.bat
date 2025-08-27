@echo off
REM Start backend in a new cmd window
start cmd /k "cd backend\src && call ..\..\venv\Scripts\activate && python main.py"
REM Start frontend in a new cmd window
start cmd /k "cd frontend && npm run dev"
