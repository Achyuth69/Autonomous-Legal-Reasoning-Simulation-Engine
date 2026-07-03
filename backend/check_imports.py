import sys
sys.path.insert(0, '.')

errors = []

def try_import(name, from_stmt):
    try:
        exec(from_stmt)
        print(f"  OK  {name}")
    except Exception as e:
        print(f"  FAIL {name}: {e}")
        errors.append(name)

print("=== Import Check ===")
try_import("fastapi", "import fastapi")
try_import("langchain", "import langchain")
try_import("langchain_google_genai", "import langchain_google_genai")
try_import("langchain_community", "import langchain_community")
try_import("groq", "import groq")
try_import("aiosqlite", "import aiosqlite")
try_import("sqlalchemy", "import sqlalchemy")
try_import("chromadb", "import chromadb")
try_import("PyPDF2", "import PyPDF2")
try_import("docx", "from docx import Document")
try_import("pdfplumber", "import pdfplumber")
try_import("aiofiles", "import aiofiles")
try_import("structlog", "import structlog")
try_import("sentence_transformers", "import sentence_transformers")

print("\n=== App Module Check ===")
try_import("config", "from app.core.config import settings")
try_import("main app", "from app.main import app")
try_import("case_intake", "from app.agents.case_intake_agent import CaseIntakeAgent")
try_import("statute", "from app.agents.statute_research_agent import StatuteResearchAgent")
try_import("caselaw", "from app.agents.caselaw_retrieval_agent import CaseLawRetrievalAgent")
try_import("plaintiff", "from app.agents.plaintiff_advocate_agent import PlaintiffAdvocateAgent")
try_import("defendant", "from app.agents.defendant_advocate_agent import DefendantAdvocateAgent")
try_import("judge", "from app.agents.judge_agent import JudgeAgent")
try_import("risk", "from app.agents.risk_analysis_agent import RiskAnalysisAgent")
try_import("citation", "from app.agents.citation_verification_agent import CitationVerificationAgent")
try_import("debate", "from app.agents.multi_model_debate_agent import MultiModelDebateAgent")
try_import("orchestrator", "from app.services.orchestrator import LegalReasoningOrchestrator")
try_import("doc_processor", "from app.services.document_processor import DocumentProcessor")

print(f"\n=== Result: {len(errors)} failures ===")
if errors:
    print("FAILED:", errors)
else:
    print("ALL OK - ready to run!")
