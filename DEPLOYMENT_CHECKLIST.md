# Deployment Checklist

Use this checklist to ensure proper deployment and configuration.

## Pre-Deployment Setup

### Google Cloud Configuration
- [ ] Google Cloud project created
- [ ] Gmail API enabled in API Library
- [ ] Google+ API enabled in API Library
- [ ] OAuth 2.0 credentials created (Web application type)
- [ ] OAuth consent screen configured
- [ ] Test user `test@gmail.com` added
- [ ] Your email added as test user
- [ ] Client ID and Client Secret saved

### API Keys
- [ ] OpenAI API key obtained (or Anthropic key)
- [ ] API key has sufficient credits
- [ ] API key permissions verified

## Backend Deployment

### Environment Variables
- [ ] `GOOGLE_CLIENT_ID` configured
- [ ] `GOOGLE_CLIENT_SECRET` configured
- [ ] `GOOGLE_REDIRECT_URI` set to production URL
- [ ] `OPENAI_API_KEY` configured
- [ ] `AI_PROVIDER` set (openai or anthropic)
- [ ] `SECRET_KEY` generated (random string)
- [ ] `FRONTEND_URL` set to Vercel URL
- [ ] `BACKEND_URL` set to backend URL
- [ ] `SESSION_EXPIRE_HOURS` configured
- [ ] `ENVIRONMENT` set to production

### Deployment Platform (Choose one)

#### Option A: Render
- [ ] Account created on render.com
- [ ] New Web Service created
- [ ] GitHub repository connected
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] All environment variables added
- [ ] Service deployed successfully
- [ ] Backend URL noted: `https://your-app.onrender.com`

#### Option B: Railway
- [ ] Account created on railway.app
- [ ] New project created from GitHub
- [ ] Environment variables added
- [ ] Build and deploy successful
- [ ] Backend URL noted

#### Option C: Heroku
- [ ] Heroku account created
- [ ] Heroku CLI installed
- [ ] App created: `heroku create app-name`
- [ ] Buildpack set: `heroku buildpacks:set heroku/python`
- [ ] Environment variables added: `heroku config:set KEY=value`
- [ ] Git remote added
- [ ] Code pushed: `git push heroku main`
- [ ] Backend URL noted

### Backend Verification
- [ ] Health endpoint accessible: `GET /health`
- [ ] API docs accessible: `GET /docs`
- [ ] CORS configured for frontend URL
- [ ] No errors in deployment logs

## Frontend Deployment

### Vercel Setup
- [ ] Vercel account created
- [ ] Vercel CLI installed: `npm install -g vercel`
- [ ] Frontend directory ready

### Deployment Steps
- [ ] Navigate to frontend folder: `cd frontend`
- [ ] Run `vercel` command
- [ ] Link to existing project or create new
- [ ] Production deployment confirmed
- [ ] Frontend URL noted: `https://your-app.vercel.app`

### Environment Variables
- [ ] Vercel dashboard opened
- [ ] Project settings accessed
- [ ] Environment variable added:
  - Name: `VITE_API_URL`
  - Value: `https://your-backend-url.com`
- [ ] Changes redeployed

### Frontend Verification
- [ ] Application loads at Vercel URL
- [ ] No console errors
- [ ] Login button visible
- [ ] UI renders correctly
- [ ] API connection working

## OAuth Configuration Update

### Google Cloud Console
- [ ] OAuth consent screen → Edit
- [ ] Authorized JavaScript origins added:
  - `https://your-app.vercel.app`
- [ ] Authorized redirect URIs added:
  - `https://your-backend-url.com/auth/callback`
  - `https://your-backend-url.onrender.com/auth/callback`
- [ ] Changes saved

## Testing

### Manual Testing
- [ ] Navigate to `https://your-app.vercel.app`
- [ ] Click "Sign in with Google"
- [ ] OAuth consent screen appears
- [ ] Grant all permissions
- [ ] Redirect to dashboard successful
- [ ] Welcome message displays with user name
- [ ] Profile picture shows (if available)

### Email Operations
- [ ] Send message: "Show me my last 5 emails"
- [ ] Emails display correctly
- [ ] AI summaries generated
- [ ] Email metadata correct (sender, subject, date)

### Reply Feature
- [ ] Click "Reply" on an email
- [ ] AI generates reply
- [ ] Reply preview shows
- [ ] Click "Send Reply"
- [ ] Success message appears
- [ ] Verify email sent in Gmail

### Delete Feature
- [ ] Click "Delete" on an email
- [ ] Confirmation modal appears
- [ ] Confirm deletion
- [ ] Success message appears
- [ ] Email removed from list
- [ ] Verify email in Gmail trash

### Error Handling
- [ ] Try invalid commands
- [ ] Error messages display properly
- [ ] Session expiration handled
- [ ] API failures show user-friendly errors

## Documentation Updates

- [ ] Main README.md updated with:
  - [ ] Live frontend URL
  - [ ] Live backend URL
  - [ ] Production environment variables
- [ ] Screenshots added (optional)
- [ ] Known issues documented

## Security Checklist

- [ ] `.env` files not committed to Git
- [ ] `.gitignore` includes sensitive files
- [ ] API keys not exposed in frontend
- [ ] HTTPS enabled on all URLs
- [ ] OAuth redirect URIs match exactly
- [ ] Session timeout configured
- [ ] CORS origins restricted appropriately

## Performance Checklist

- [ ] Frontend build optimized
- [ ] API response times acceptable
- [ ] No unnecessary re-renders
- [ ] Images optimized (if any)
- [ ] Bundle size reasonable

## Monitoring & Logging

- [ ] Backend logs accessible
- [ ] Error tracking setup (optional)
- [ ] Usage monitoring (optional)
- [ ] API rate limits understood

## Submission Checklist

- [ ] GitHub repository public
- [ ] All code committed and pushed
- [ ] README.md complete with:
  - [ ] Live demo URL
  - [ ] Setup instructions
  - [ ] Environment variables documented
  - [ ] Test user information
  - [ ] Technologies used
  - [ ] Known limitations
- [ ] QUICKSTART.md included
- [ ] PROJECT_SUMMARY.md included
- [ ] Code is readable and commented
- [ ] No hardcoded credentials
- [ ] License file (if required)

## Testing with Reviewer Account

### Setup for Reviewer
- [ ] `test@gmail.com` added as test user in Google Console
- [ ] Reviewer can access OAuth consent screen
- [ ] Reviewer can grant permissions
- [ ] Reviewer can perform all operations

### Expected Flow for Reviewer
1. Visit `https://your-app.vercel.app`
2. Click "Sign in with Google"
3. Login with `test@gmail.com`
4. Grant permissions
5. See dashboard with welcome message
6. Type: "Show me my last 5 emails"
7. See emails with AI summaries
8. Click "Reply" on any email
9. See generated reply
10. Click "Send Reply"
11. See success message
12. Click "Delete" on any email
13. Confirm deletion
14. See success message

## Troubleshooting Common Issues

### OAuth Error: redirect_uri_mismatch
- [ ] Verify redirect URI in Google Console matches exactly
- [ ] Check for trailing slashes
- [ ] Ensure http vs https matches

### CORS Errors
- [ ] Verify FRONTEND_URL in backend .env
- [ ] Check CORS middleware configuration
- [ ] Verify Vercel URL is correct

### Session Expired
- [ ] Check SESSION_EXPIRE_HOURS setting
- [ ] Verify session store working
- [ ] Test logout and login again

### AI Service Errors
- [ ] Verify API key validity
- [ ] Check API credit balance
- [ ] Review rate limits
- [ ] Check model availability

## Final Verification

- [ ] All features working end-to-end
- [ ] No console errors
- [ ] No backend errors in logs
- [ ] Documentation accurate
- [ ] Repository clean and organized
- [ ] README has correct live URLs

## Post-Deployment

- [ ] Monitor application for 24 hours
- [ ] Check error logs
- [ ] Verify API usage
- [ ] Test from different browsers
- [ ] Test from mobile device (optional)
- [ ] Gather feedback

---

## Support Contacts

- **Google Cloud Support**: https://cloud.google.com/support
- **Vercel Support**: https://vercel.com/support
- **Render Support**: https://render.com/docs
- **OpenAI Support**: https://help.openai.com/

## Additional Resources

- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Vercel Documentation](https://vercel.com/docs)

---

**Status**: ⬜ Not Started | 🟡 In Progress | ✅ Complete

Update status as you complete each item!
