# Backend - AI Email Assistant

FastAPI backend for the AI Email Assistant application.

## Features

- Google OAuth2 authentication with Gmail API integration
- RESTful API endpoints for email operations
- AI-powered email summaries and response generation
- Session management
- Comprehensive error handling

## Tech Stack

- **FastAPI** - Modern Python web framework
- **Google APIs** - Gmail and OAuth integration
- **OpenAI/Anthropic** - AI text generation
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

## API Endpoints

### Authentication
- `GET /auth/login` - Start OAuth flow
- `GET /auth/callback` - OAuth callback handler
- `POST /auth/logout` - End user session
- `GET /auth/session/{session_id}` - Get session info

### Chatbot
- `POST /chatbot/message` - Send message to AI assistant
- `GET /chatbot/welcome/{session_id}` - Get welcome message

### Email Operations
- `POST /email/generate-reply` - Generate AI reply
- `POST /email/send-reply` - Send email reply
- `POST /email/delete` - Delete email
- `GET /email/details/{email_id}` - Get email details

## Development

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Server
```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Run Tests
```bash
pytest tests/ -v
```

## Environment Variables

See `.env.example` for required environment variables.

Key variables:
- `GOOGLE_CLIENT_ID` - From Google Cloud Console
- `GOOGLE_CLIENT_SECRET` - From Google Cloud Console
- `OPENAI_API_KEY` - From OpenAI dashboard
- `SECRET_KEY` - Random string for session security

## Architecture

```
app/
├── auth/           # Authentication and session management
│   ├── google_oauth.py
│   └── session.py
├── services/       # Business logic
│   ├── gmail_service.py
│   └── ai_service.py
├── models/         # Pydantic schemas
│   └── schemas.py
├── routers/        # API endpoints
│   ├── auth.py
│   ├── chatbot.py
│   └── email.py
├── config.py       # Settings
└── main.py         # FastAPI application
```

## Security

- OAuth tokens stored in-memory (upgrade to Redis for production)
- All endpoints require valid session
- CORS configured for frontend access
- Environment variables for sensitive data

## Deployment

### Render
1. Create new Web Service
2. Connect repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables

### Heroku
1. Create app: `heroku create your-app-name`
2. Set buildpack: `heroku buildpacks:set heroku/python`
3. Add config vars: `heroku config:set KEY=value`
4. Deploy: `git push heroku main`

## Logging

Application uses Python's built-in logging:
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Message")
```

Logs include:
- Authentication events
- API requests
- Errors and exceptions
- Gmail API calls

## Error Handling

- HTTP exceptions return JSON with error details
- Gmail API errors caught and logged
- AI service errors handled gracefully
- Session validation on all protected endpoints
