# Quick Start Guide

Get the AI Email Assistant running in 5 minutes!

## Prerequisites

- Python 3.11+
- Node.js 18+
- Google Cloud account
- OpenAI API key

## Step 1: Google Cloud Setup (5 min)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project
3. Enable "Gmail API" and "Google+ API"
4. Create OAuth 2.0 credentials (Web application)
5. Add redirect URI: `http://localhost:8000/auth/callback`
6. Save Client ID and Secret
7. Add test user: `test@gmail.com`

## Step 2: Backend Setup (2 min)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your credentials
# - GOOGLE_CLIENT_ID=your_client_id
# - GOOGLE_CLIENT_SECRET=your_client_secret
# - OPENAI_API_KEY=your_openai_key

# Run server
uvicorn app.main:app --reload
```

Backend will run at `http://localhost:8000`

## Step 3: Frontend Setup (2 min)

```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Edit .env
# VITE_API_URL=http://localhost:8000

# Run frontend
npm run dev
```

Frontend will run at `http://localhost:5173`

## Step 4: Test the App (1 min)

1. Open `http://localhost:5173`
2. Click "Sign in with Google"
3. Grant Gmail permissions
4. Try: "Show me my last 5 emails"

## Common Commands

### Read Emails
- "Show me my last 5 emails"
- "Read my recent emails"

### Reply to Email
1. First read emails
2. Click "Reply" button
3. Review generated response
4. Click "Send Reply"

### Delete Email
1. Read emails
2. Click "Delete" button
3. Confirm deletion

## Troubleshooting

### Backend won't start
- Check Python version: `python --version`
- Verify virtual environment is activated
- Check `.env` file exists and has all variables

### Frontend won't start
- Check Node version: `node --version`
- Delete `node_modules` and run `npm install` again
- Verify `.env` file has correct backend URL

### OAuth errors
- Verify redirect URI matches exactly in Google Console
- Check if Gmail API is enabled
- Ensure test user is added

### AI errors
- Verify OpenAI API key is valid
- Check API credit balance
- Try using Anthropic instead (update `.env`)

## Next Steps

- Read [README.md](README.md) for full documentation
- Deploy to production (Vercel + Render)
- Customize AI prompts in [backend/app/services/ai_service.py](backend/app/services/ai_service.py)
- Add more features!

## Support

Check the main README.md for:
- Detailed setup instructions
- Deployment guide
- API documentation
- Architecture overview
