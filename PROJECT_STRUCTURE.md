# Project Structure

Complete file structure of the AI Email Assistant project.

```
ai-email-assistant/
│
├── README.md                          # Main documentation
├── QUICKSTART.md                      # Quick setup guide
├── PROJECT_SUMMARY.md                 # Project overview
├── DEPLOYMENT_CHECKLIST.md            # Deployment guide
├── PROJECT_STRUCTURE.md               # This file
├── setup.sh                           # Automated setup script
├── .gitignore                         # Git ignore rules
│
├── backend/                           # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI application entry point
│   │   ├── config.py                  # Configuration and settings
│   │   │
│   │   ├── auth/                      # Authentication module
│   │   │   ├── __init__.py
│   │   │   ├── google_oauth.py        # Google OAuth implementation
│   │   │   └── session.py             # Session management
│   │   │
│   │   ├── services/                  # Business logic services
│   │   │   ├── __init__.py
│   │   │   ├── gmail_service.py       # Gmail API operations
│   │   │   └── ai_service.py          # AI text generation
│   │   │
│   │   ├── models/                    # Data models
│   │   │   ├── __init__.py
│   │   │   └── schemas.py             # Pydantic schemas
│   │   │
│   │   └── routers/                   # API endpoints
│   │       ├── __init__.py
│   │       ├── auth.py                # Authentication routes
│   │       ├── chatbot.py             # Chatbot routes
│   │       └── email.py               # Email operation routes
│   │
│   ├── tests/                         # Backend tests
│   │   ├── __init__.py
│   │   └── test_auth.py               # Authentication tests
│   │
│   ├── requirements.txt               # Python dependencies
│   ├── .env.example                   # Environment template
│   ├── Procfile                       # Heroku deployment
│   ├── runtime.txt                    # Python version
│   └── README.md                      # Backend documentation
│
└── frontend/                          # React Frontend
    ├── public/                        # Static assets
    │
    ├── src/
    │   ├── components/                # React components
    │   │   ├── Login.jsx              # Login page
    │   │   ├── Dashboard.jsx          # Main dashboard
    │   │   └── ChatBot.jsx            # Chatbot interface
    │   │
    │   ├── contexts/                  # React contexts
    │   │   └── AuthContext.jsx        # Authentication state
    │   │
    │   ├── services/                  # API clients
    │   │   └── api.js                 # Backend API service
    │   │
    │   ├── App.jsx                    # Main app component
    │   ├── main.jsx                   # Entry point
    │   └── index.css                  # Global styles
    │
    ├── index.html                     # HTML template
    ├── package.json                   # Node dependencies
    ├── vite.config.js                 # Vite configuration
    ├── vercel.json                    # Vercel deployment config
    └── .env.example                   # Environment template
```

## Key Files Description

### Documentation Files
- **README.md**: Complete setup, deployment, and usage guide
- **QUICKSTART.md**: 5-minute quick start instructions
- **PROJECT_SUMMARY.md**: Technical overview and features
- **DEPLOYMENT_CHECKLIST.md**: Step-by-step deployment guide
- **PROJECT_STRUCTURE.md**: This file structure document

### Configuration Files
- **backend/.env.example**: Template for backend environment variables
- **frontend/.env.example**: Template for frontend environment variables
- **backend/config.py**: Centralized configuration management
- **vite.config.js**: Vite build and dev server configuration
- **vercel.json**: Vercel deployment settings

### Backend Core Files
- **app/main.py**: FastAPI application, CORS, error handlers
- **app/auth/google_oauth.py**: OAuth flow, token management
- **app/auth/session.py**: In-memory session store
- **app/services/gmail_service.py**: Gmail API wrapper
- **app/services/ai_service.py**: OpenAI/Anthropic integration
- **app/models/schemas.py**: Request/response models
- **app/routers/*.py**: API endpoint definitions

### Frontend Core Files
- **src/App.jsx**: Main app with routing
- **src/components/Login.jsx**: Login page with OAuth button
- **src/components/Dashboard.jsx**: Main dashboard layout
- **src/components/ChatBot.jsx**: Chat interface and email operations
- **src/contexts/AuthContext.jsx**: Global auth state management
- **src/services/api.js**: Axios-based API client
- **src/index.css**: Complete application styling

## File Statistics

### Backend
- Python files: 13
- Lines of code: ~1,500+
- Test files: 1
- Dependencies: 18

### Frontend
- JavaScript/JSX files: 7
- Lines of code: ~1,200+
- Dependencies: 6
- CSS lines: ~800+

### Documentation
- Markdown files: 5
- Total documentation: ~2,000+ lines

## Module Dependencies

### Backend Flow
```
main.py
  ├─> routers/auth.py
  │     ├─> auth/google_oauth.py
  │     └─> auth/session.py
  │
  ├─> routers/chatbot.py
  │     ├─> auth/session.py
  │     ├─> services/gmail_service.py
  │     └─> services/ai_service.py
  │
  └─> routers/email.py
        ├─> auth/session.py
        ├─> services/gmail_service.py
        └─> services/ai_service.py
```

### Frontend Flow
```
main.jsx
  └─> App.jsx
        ├─> contexts/AuthContext.jsx
        │     └─> services/api.js
        │
        ├─> components/Login.jsx
        │     └─> services/api.js
        │
        └─> components/Dashboard.jsx
              └─> components/ChatBot.jsx
                    ├─> contexts/AuthContext.jsx
                    └─> services/api.js
```

## API Endpoints

### Authentication
- `GET /auth/login` - Initiate OAuth
- `GET /auth/callback` - OAuth callback
- `POST /auth/logout` - Logout
- `GET /auth/session/{id}` - Get session

### Chatbot
- `POST /chatbot/message` - Send message
- `GET /chatbot/welcome/{id}` - Welcome message

### Email
- `POST /email/generate-reply` - Generate AI reply
- `POST /email/send-reply` - Send reply
- `POST /email/delete` - Delete email
- `GET /email/details/{id}` - Get email details

## Environment Variables

### Backend (.env)
```
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI
OPENAI_API_KEY
AI_PROVIDER
SECRET_KEY
FRONTEND_URL
BACKEND_URL
SESSION_EXPIRE_HOURS
ENVIRONMENT
```

### Frontend (.env)
```
VITE_API_URL
```

## Build Commands

### Backend
```bash
# Install
pip install -r requirements.txt

# Run dev
uvicorn app.main:app --reload

# Run prod
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Test
pytest tests/ -v
```

### Frontend
```bash
# Install
npm install

# Run dev
npm run dev

# Build
npm run build

# Preview
npm run preview
```

## Deployment Targets

### Frontend
- **Primary**: Vercel (configured via vercel.json)
- **Alternative**: Netlify, GitHub Pages

### Backend
- **Primary**: Render (configured via Procfile)
- **Alternative**: Railway, Heroku, AWS, Google Cloud Run

## Code Quality Features

- Type hints in Python code
- PropTypes/TypeScript potential
- Comprehensive docstrings
- Error handling throughout
- Logging in backend
- Code organization by feature
- Reusable components
- Separation of concerns
- Environment-based configuration

## Testing Coverage

- Authentication: Session management tests
- Services: Unit tests for core functionality
- Integration: End-to-end manual testing
- Documentation: Complete testing checklist

## Security Measures

- OAuth 2.0 authentication
- Environment variables for secrets
- CORS configuration
- Session timeout
- Input validation (Pydantic)
- SQL injection prevention (ORM)
- XSS prevention (React)
- Secure token storage

---

This structure ensures maintainability, scalability, and clear separation of concerns.
