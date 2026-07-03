# Quick Start Guide

Get the Autonomous Legal Reasoning Engine up and running in 5 minutes!

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (or use Docker)
- Google Gemini API Key (free — get one at https://aistudio.google.com/app/apikey)
- Groq API Key (optional, for Multi-Model Debate — free at console.groq.com)

## Option 1: Docker Compose (Recommended)

The easiest way to run the entire application:

```bash
# 1. Clone the repository
git clone https://github.com/Achyuth69/Autonomous-Legal-Reasoning-Simulation-Engine.git
cd Autonomous-Legal-Reasoning-Simulation-Engine

# 2. Add your Gemini API key to backend/.env (FREE at aistudio.google.com)
cp backend/.env.example backend/.env
# Edit backend/.env and add: GEMINI_API_KEY=your-key-here

# 3. Start everything with Docker Compose
docker-compose up --build
```

That's it! Access the application at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Option 2: Manual Setup

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file and add your Gemini API key
cp .env.example .env
# Edit .env and add: GEMINI_API_KEY=your-key-here
# Get a FREE key at: https://aistudio.google.com/app/apikey

# Create data directories
mkdir -p data/uploads
mkdir -p data/chroma

# Run the backend
uvicorn app.main:app --reload
```

Backend will be available at http://localhost:8000

### Frontend Setup

Open a new terminal:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env.local
cp .env.example .env.local

# Run the frontend
npm run dev
```

Frontend will be available at http://localhost:3000

## Exploring Multi-Model AI Debate

The debate feature uses Groq's free API to pit multiple AI models against each other:

1. Get a free Groq API key at https://console.groq.com
2. Add it to `backend/.env`:
   ```bash
   GROQ_API_KEY=your-groq-api-key-here
   GROQ_DEBATE_ROUNDS=3
   GROQ_MODELS=llama3-70b-8192,mixtral-8x7b-32768,gemma2-9b-it
   ```
3. After case analysis completes, click the **AI Debate** tab
4. You'll see each model's argument per round and the final consensus

The models currently supported in debate:
- **Llama 3 70B** – Meta's flagship model
- **Mixtral 8x7B** – Mistral's mixture-of-experts model
- **Gemma 2 9B** – Google's efficient model

## Testing the Application

1. Open http://localhost:3000 in your browser

2. Click "New Case" or "Upload Your First Case"

3. Upload a legal document:
   - Use the sample case in `sample-documents/sample-case.txt`
   - Or upload your own PDF/DOCX/TXT file

4. Wait for the AI agents to process the case (1-3 minutes)

5. Explore the results:
   - **Overview**: Case summary and verdict
   - **Facts & Issues**: Extracted facts and legal issues
   - **Arguments**: Plaintiff and defendant positions
   - **Judgment**: Simulated judicial decision
   - **Risk Analysis**: Litigation risk assessment
   - **AI Debate**: Multi-model debate and consensus (if Groq configured)
   - **Agent Logs**: AI reasoning traces

## API Examples

### Upload a Case

```bash
curl -X POST http://localhost:8000/api/v1/cases/upload \
  -F "file=@sample-documents/sample-case.txt" \
  -F "title=Sample Negligence Case"
```

### Get Case Details

```bash
curl http://localhost:8000/api/v1/cases/{case_id}
```

### List All Cases

```bash
curl http://localhost:8000/api/v1/cases/
```

## Configuration

### Environment Variables

**Backend (.env):**
- `GEMINI_API_KEY`: Your free Google Gemini API key (required — get at aistudio.google.com)
- `GEMINI_MODEL`: Model to use (default: `gemini-1.5-flash`)
- `GROQ_API_KEY`: Your Groq API key (optional, enables multi-model debate)
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_MODEL`: Model to use (default: gpt-4-turbo-preview)
- `DEBUG`: Enable debug mode (default: True)

**Frontend (.env.local):**
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)

## Troubleshooting

### Backend won't start

**Issue**: `google.auth.exceptions.DefaultCredentialsError` or `No API key provided`
**Solution**: Add your Gemini API key to `backend/.env`: `GEMINI_API_KEY=...`

**Issue**: Database connection error
**Solution**: Make sure PostgreSQL is running or use Docker Compose

### Frontend can't connect to backend

**Issue**: CORS errors in browser console
**Solution**: Check that backend is running on port 8000

### File upload fails

**Issue**: "File type not supported"
**Solution**: Ensure you're uploading PDF, DOCX, or TXT files

### Processing takes too long

**Issue**: Case stuck in "processing" status
**Solution**: 
- Check backend logs for errors
- Verify Gemini API key is valid
- Ensure sufficient API quota (Gemini has generous free tier)

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# With coverage
pytest --cov=app tests/
```

### Code Quality

```bash
# Backend linting
cd backend
black app/
flake8 app/

# Frontend linting
cd frontend
npm run lint
```

### Database Migration

```bash
cd backend
python -m app.db.init_db
```

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Check [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- Explore the API at http://localhost:8000/docs
- Try different legal cases and document types
- Customize agents in `backend/app/agents/`

## Need Help?

- Open an issue on GitHub
- Check the API documentation at `/docs`
- Review agent logs for debugging

## Security Note

⚠️ **Important**: This is a demonstration system. Do not use for actual legal advice or production legal work without proper review and validation.
