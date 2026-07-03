# Quick Setup Guide - No PostgreSQL/Redis Required!

## What You Need

1. **Python 3.11+** - [Download here](https://www.python.org/downloads/)
2. **Node.js 18+** - [Download here](https://nodejs.org/)
3. **Google Gemini API Key** - FREE at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
4. **Groq API Key** (optional) - FREE at [console.groq.com](https://console.groq.com)

## Step 1: Get API Keys (2 minutes)

### Get Gemini Key (Required - 100% Free)
1. Go to https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key

### Get Groq Key (Optional for multi-model debate - Also Free)
1. Go to https://console.groq.com
2. Sign up
3. Go to API Keys section
4. Create key and copy it

## Step 2: Setup Backend (3 minutes)

```bash
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Configure Environment (1 minute)

Open `backend/.env` and add your keys:

```bash
# Required - Add your Gemini key here
GEMINI_API_KEY=AIza...your-key-here

# Optional - Add for multi-model debate feature
GROQ_API_KEY=gsk_...your-key-here

# Everything else is already configured with SQLite (no database setup needed!)
```

**That's it!** The database is SQLite (a simple file) - no PostgreSQL needed.

## Step 4: Setup Frontend (2 minutes)

Open a NEW terminal window:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install
```

## Step 5: Run Everything (30 seconds)

### Terminal 1 - Backend:
```bash
cd backend
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Mac/Linux
uvicorn app.main:app --reload
```

Wait for: `Application startup complete.`

### Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

Wait for: `Local: http://localhost:3000`

## Step 6: Open and Test

1. Open browser to **http://localhost:3000**
2. Click "New Case" or "Upload Your First Case"
3. Upload the sample: `sample-documents/sample-case.txt`
4. Wait 2-3 minutes for AI analysis
5. Explore all tabs:
   - Overview
   - Facts & Issues
   - Arguments (Plaintiff vs Defendant)
   - Judgment
   - Risk Analysis
   - **AI Debate** (if you added Groq key)
   - Agent Logs

## Troubleshooting

### Backend won't start

**Error**: `No module named 'app'`
**Fix**: Make sure you're in the `backend` folder and venv is activated

**Error**: `GEMINI_API_KEY not found`
**Fix**: Add your key to `backend/.env` file

**Error**: `google.auth.exceptions.DefaultCredentialsError`
**Fix**: Your API key is invalid - get a new one from aistudio.google.com

### Frontend won't start

**Error**: `Cannot find module`
**Fix**: Run `npm install` in the frontend folder

**Error**: `Port 3000 already in use`
**Fix**: Kill the process using port 3000 or use a different port: `npm run dev -- -p 3001`

### Case processing fails

**Error**: Case stuck in "processing"
**Fix**: 
- Check backend terminal for error messages
- Verify your Gemini API key is correct
- Try with a smaller document first

## What's Different from Standard Setup?

✅ **SQLite instead of PostgreSQL** - No database server needed, just a file in `backend/data/`
✅ **No Redis** - Not required for core functionality
✅ **Gemini (free) instead of OpenAI (paid)** - Completely free to use
✅ **Everything runs locally** - No cloud services needed

## Database Files

The SQLite database is stored at:
```
backend/data/legal_reasoning.db
```

To reset everything, just delete this file and restart the backend.

## Available Models

### Main Analysis (Gemini)
- Default: `gemini-1.5-flash` (fast, free, great for most cases)
- Alternative: `gemini-1.5-pro` (slower but more accurate)

Change in `backend/.env`:
```bash
GEMINI_MODEL=gemini-1.5-flash  # or gemini-1.5-pro
```

### Multi-Model Debate (Groq)
- Llama 3 70B
- Mixtral 8x7B
- Gemma 2 9B

## Next Steps

1. Try uploading your own legal documents (PDF, DOCX, TXT)
2. Experiment with different cases
3. Read the full documentation in README.md
4. Check out the AI Debate feature if you configured Groq

## Need Help?

- API documentation: http://localhost:8000/docs (when backend is running)
- Sample case: `sample-documents/sample-case.txt`
- Full guide: See QUICKSTART.md

## Pro Tips

1. **Gemini Flash is fast** - Most cases process in 1-3 minutes
2. **Debate feature** - Adds an extra minute but gives multiple AI perspectives
3. **Upload size limit** - 10MB max, increase in `backend/.env` if needed
4. **Rate limits** - Gemini free tier is generous (60 requests/minute)
5. **Data persistence** - All cases are saved in the SQLite database

Enjoy analyzing legal cases with AI! 🚀⚖️
