# AI Email Assistant

A powerful AI-powered email management system that integrates with Gmail to help you read, respond to, and manage your emails through an intelligent chatbot interface.

## 🌐 Live Demo

**Frontend URL:** `https://your-app-name.vercel.app` (Update after deployment)
**Backend URL:** `https://your-backend-url.com` (Update after deployment)

## ✨ Features

### Core Functionality
- **Google OAuth Authentication** - Secure login with Gmail permissions
- **AI-Powered Email Summaries** - Get concise summaries of your emails
- **Smart Email Replies** - Generate professional, context-aware responses
- **Email Management** - Delete unwanted emails with confirmation
- **Natural Language Interface** - Chat naturally with the AI assistant

### User Experience
- Clean, modern UI with responsive design
- Real-time conversation interface
- Confirmation dialogs for destructive actions
- Error handling with user-friendly messages
- Session management with automatic token refresh

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI 0.109.0
- **Authentication:** Google OAuth2 (google-auth-oauthlib)
- **Email API:** Gmail API (google-api-python-client)
- **AI Provider:** OpenAI GPT-4-Turbo (or Anthropic Claude)
- **Session Storage:** In-memory (can be upgraded to Redis)

### Frontend
- **Framework:** React 18 with Vite
- **Routing:** React Router DOM
- **HTTP Client:** Axios
- **Styling:** Custom CSS

### Deployment
- **Frontend:** Vercel (free tier)
- **Backend:** Render/Railway/Heroku (any Python hosting)

## 📋 Prerequisites

Before setting up the project, ensure you have:

1. **Python 3.11+** installed
2. **Node.js 18+** and npm installed
3. **Google Cloud Project** with Gmail API enabled
4. **OpenAI API key** (or Anthropic API key)

## 🔧 Setup Instructions

### Part 1: Google Cloud Configuration

1. **Create a Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Gmail API**
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it
   - Also enable "Google+ API" for user profile info

3. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Web application"
   - Add authorized redirect URIs:
     - `http://localhost:8000/auth/callback` (for local development)
     - `https://your-backend-url.com/auth/callback` (for production)
   - Save the **Client ID** and **Client Secret**

4. **Add Test Users**
   - Go to "APIs & Services" > "OAuth consent screen"
   - Under "Test users", add `testingcheckuser1234@gmail.com`
   - Also add your own email for testing

### Part 2: Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv

   # On Windows:
   venv\Scripts\activate

   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file**
   ```bash
   cp .env.example .env
   ```

5. **Configure environment variables** in `.env`:
   ```env
   # Google OAuth Configuration
   GOOGLE_CLIENT_ID=your_google_client_id_here.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your_google_client_secret_here
   GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback

   # AI Provider Configuration
   OPENAI_API_KEY=sk-your-openai-api-key-here
   AI_PROVIDER=openai

   # Application Configuration
   SECRET_KEY=your-secret-key-generate-a-random-string
   FRONTEND_URL=http://localhost:5173
   BACKEND_URL=http://localhost:8000

   # Session Configuration
   SESSION_EXPIRE_HOURS=24

   # Environment
   ENVIRONMENT=development
   ```

6. **Run the backend server**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

   The API will be available at `http://localhost:8000`
   API documentation at `http://localhost:8000/docs`

### Part 3: Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Create `.env` file**
   ```bash
   cp .env.example .env
   ```

4. **Configure environment variables** in `.env`:
   ```env
   VITE_API_URL=http://localhost:8000
   ```

5. **Run the development server**
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:5173`

## 🚀 Deployment

### Deploy Frontend to Vercel

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy from frontend directory**
   ```bash
   cd frontend
   vercel
   ```

3. **Configure environment variables in Vercel**
   - Go to your project settings on Vercel dashboard
   - Add environment variable: `VITE_API_URL=https://your-backend-url.com`

4. **Get your live URL**
   - After deployment, Vercel will provide a URL like: `https://your-app-name.vercel.app`

### Deploy Backend (Example: Render)

1. **Create a new Web Service** on [Render](https://render.com/)

2. **Connect your GitHub repository**

3. **Configure build settings:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Add environment variables:**
   - All variables from your `.env` file
   - Update `FRONTEND_URL` to your Vercel URL
   - Update `GOOGLE_REDIRECT_URI` to `https://your-backend-url.onrender.com/auth/callback`

5. **Update Google Cloud OAuth**
   - Add your production redirect URI to Google Cloud Console
   - Add the Vercel URL to authorized JavaScript origins

## 📖 Usage Guide

### Basic Operations

1. **Login**
   - Click "Sign in with Google"
   - Grant Gmail permissions
   - You'll be redirected to the dashboard

2. **Read Emails**
   - Type: "Show me my last 5 emails"
   - Or: "Read my recent emails"
   - The AI will fetch and summarize your emails

3. **Reply to Email**
   - After viewing emails, click "Reply" on any email
   - The AI generates a professional response
   - Review and click "Send Reply" to send

4. **Delete Email**
   - Click "Delete" on any email
   - Confirm the deletion in the modal
   - Email will be moved to trash

5. **Natural Language Commands**
   - "Show me emails from john@example.com"
   - "Help me reply to the email from Sarah"
   - "Delete the spam emails"

## 🔒 Security Considerations

- OAuth tokens are stored in-memory (upgrade to Redis for production)
- All API endpoints require valid session authentication
- Sensitive operations (delete, send) require confirmation
- HTTPS required for production deployment
- Environment variables never exposed to client

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Manual Testing Checklist
- [ ] Google OAuth login flow
- [ ] Fetch and display emails
- [ ] AI summarization works
- [ ] Generate reply for email
- [ ] Send reply successfully
- [ ] Delete email with confirmation
- [ ] Session expiration handling
- [ ] Error messages display correctly

## 📁 Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── auth/           # Authentication logic
│   │   ├── services/       # Gmail and AI services
│   │   ├── models/         # Pydantic models
│   │   ├── routers/        # API endpoints
│   │   ├── config.py       # Configuration
│   │   └── main.py         # FastAPI app
│   ├── tests/              # Backend tests
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment template
│
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── contexts/       # React contexts
│   │   ├── services/       # API clients
│   │   ├── App.jsx         # Main app
│   │   └── main.jsx        # Entry point
│   ├── package.json        # Node dependencies
│   ├── vite.config.js      # Vite configuration
│   └── vercel.json         # Vercel deployment config
│
└── README.md               # This file
```

## 🐛 Troubleshooting

### Common Issues

**1. "Invalid session" error**
- Solution: Session expired. Logout and login again.

**2. "Failed to fetch emails"**
- Check if Gmail API is enabled in Google Cloud
- Verify OAuth credentials are correct
- Ensure proper scopes are requested

**3. "AI service error"**
- Verify your OpenAI/Anthropic API key is valid
- Check if you have sufficient API credits
- Review API rate limits

**4. CORS errors**
- Update `FRONTEND_URL` in backend `.env`
- Ensure frontend URL is in CORS allowed origins
- Check browser console for specific CORS errors

**5. OAuth redirect errors**
- Verify redirect URI matches exactly in Google Cloud Console
- Check for trailing slashes or http vs https mismatches

## 🔄 Future Enhancements

### Implemented
- ✅ Google OAuth authentication
- ✅ Read and summarize emails
- ✅ AI-generated replies
- ✅ Delete emails
- ✅ Natural language interface

### Potential Improvements
- [ ] Redis for session storage
- [ ] Email search and filters
- [ ] Schedule email sending
- [ ] Email templates
- [ ] Multi-language support
- [ ] Email analytics dashboard
- [ ] Attachment handling
- [ ] Email labels/categories
- [ ] Push notifications
- [ ] Dark mode

## 📝 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

- `GET /auth/login` - Initiate OAuth flow
- `GET /auth/callback` - OAuth callback
- `POST /chatbot/message` - Send message to chatbot
- `POST /email/generate-reply` - Generate AI reply
- `POST /email/send-reply` - Send email reply
- `POST /email/delete` - Delete email

## 🤝 Contributing

This is a demonstration project. For production use, consider:
- Implementing proper database for session storage
- Adding comprehensive test coverage
- Setting up CI/CD pipelines
- Implementing rate limiting
- Adding monitoring and logging
- Handling edge cases more robustly

## 📄 License

This project is for demonstration purposes.

## 👤 Author

Created as part of a technical assessment demonstrating:
- Full-stack development skills
- API integration (Google OAuth, Gmail API)
- AI integration (OpenAI/Anthropic)
- Modern React patterns
- FastAPI best practices
- Deployment and DevOps

## 🙏 Acknowledgments

- Google Gmail API
- OpenAI GPT-4
- FastAPI framework
- React and Vite
- Vercel for hosting

---

**Note:** Remember to update the live URL in this README after deployment and add `testingcheckuser1234@gmail.com` as a test user in your Google Cloud OAuth consent screen.