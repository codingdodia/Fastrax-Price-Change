# Vercel Deployment Instructions

This project contains both a React frontend and Python Flask backend that can be deployed together on Vercel.

## Prerequisites

1. Vercel CLI installed: `npm i -g vercel`
2. GitHub repository connected to Vercel

## Project Structure

```
├── frontend/          # React + Vite frontend
├── backend/src/       # Python Flask backend
├── vercel.json        # Vercel configuration
└── .vercelignore      # Files to ignore during deployment
```

## Deployment Steps

### Option 1: GitHub Integration (Recommended)

1. Push your code to GitHub
2. Connect your repository to Vercel via the dashboard
3. Vercel will automatically deploy on every push to main branch

### Option 2: Vercel CLI

1. Run `vercel` in the project root
2. Follow the prompts to deploy

## Configuration

### Environment Variables

The frontend automatically detects the environment:
- **Development**: Uses `http://localhost:5000` for API calls
- **Production**: Uses `/api` prefix for API calls

### API Routes

All backend routes are prefixed with `/api/` in production:
- `/api/upload` - File upload endpoint
- `/api/Login` - Authentication endpoint  
- `/api/fetch_products_data` - Data fetching endpoint
- And all other existing routes...

### Build Process

1. Frontend builds with Vite to `frontend/dist/`
2. Backend runs through Vercel's Python runtime
3. Static files served from frontend build
4. API routes handled by Python functions

## File Changes Made for Deployment

1. **`vercel.json`** - Main configuration file
2. **Frontend API config** - `src/config/api.ts` for environment-aware API calls
3. **Environment files** - `.env.development` and `.env.production`
4. **Backend entry point** - `backend/src/api.py` for Vercel compatibility
5. **Updated imports** - All frontend files now use the API config

## Troubleshooting

- Check Vercel function logs for backend errors
- Ensure all Python dependencies are in `backend/src/requirements.txt`
- Frontend build errors will show in Vercel build logs
- API calls should use `/api/` prefix in production

## Local Development

- Frontend: `cd frontend && npm run dev`
- Backend: `cd backend/src && python main.py`
- The frontend will proxy API calls to localhost:5000 in development