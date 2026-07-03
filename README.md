# Autonomous Legal Reasoning Simulation Engine

An intelligent multi-agent legal reasoning system capable of simulating how legal professionals analyze, interpret, debate, and resolve legal cases.

## Project Vision

Develop an AI system that demonstrates advanced reasoning through autonomous legal analysis, argument generation, precedent retrieval, statutory interpretation, risk assessment, and judgment simulation. This system emulates a virtual legal chamber where specialized AI agents collaborate and challenge one another before reaching legally reasoned conclusions.

## Core AI Agents

1. **Case Intake Agent** - Extracts facts, parties, timeline, jurisdiction, and legal issues
2. **Statute Research Agent** - Identifies relevant legal provisions
3. **Case Law Retrieval Agent** - Retrieves and ranks similar precedents
4. **Legal Reasoning Agent** - Applies statutes and precedents with step-by-step logic
5. **Plaintiff Advocate Agent** - Generates arguments supporting the plaintiff
6. **Defendant Advocate Agent** - Generates counterarguments
7. **Judge Agent** - Reviews both sides and produces detailed judgments
8. **Compliance Agent** - Checks regulatory compliance
9. **Risk Analysis Agent** - Predicts litigation risks
10. **Citation Verification Agent** - Validates legal citations

## Features

- Multi-agent collaboration with autonomous reasoning
- Legal argument generation and statutory interpretation
- Precedent comparison and citation verification
- Explainable AI with confidence estimation
- Document upload (PDF, DOCX, TXT) with OCR support
- Interactive chat interface
- Comprehensive legal reports and judgments
- Timeline and evidence visualization

## Technology Stack

- **Frontend**: Next.js, React, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python
- **Database**: PostgreSQL
- **Vector Database**: ChromaDB
- **LLM Framework**: LangGraph, LangChain
- **Document Processing**: PyPDF2, python-docx, pytesseract

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL
- Docker (optional)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Achyuth69/Autonomous-Legal-Reasoning-Simulation-Engine.git
cd Autonomous-Legal-Reasoning-Simulation-Engine
```

2. Install backend dependencies:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd ../frontend
npm install
```

4. Set up environment variables:
```bash
# Backend (.env)
cp .env.example .env
# Configure your OpenAI API key, database credentials, etc.

# Frontend (.env.local)
cp .env.example .env.local
```

5. Initialize the database:
```bash
cd ../backend
python -m app.db.init_db
```

### Running the Application

**Backend:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

Visit `http://localhost:3000` to access the application.

### Docker Deployment

```bash
docker-compose up --build
```

## Project Structure

```
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── agents/         # AI agent implementations
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configuration
│   │   ├── db/             # Database models and setup
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utility functions
│   ├── tests/              # Backend tests
│   └── requirements.txt
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js app directory
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities and API clients
│   │   └── types/         # TypeScript types
│   └── package.json
└── docker-compose.yml
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

**Backend:**
```bash
cd backend
pytest
```

**Frontend:**
```bash
cd frontend
npm test
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please read CONTRIBUTING.md for guidelines.

## Disclaimer

This system is for educational and demonstrative purposes. It does not replace professional legal advice. Always consult qualified legal professionals for actual legal matters.
