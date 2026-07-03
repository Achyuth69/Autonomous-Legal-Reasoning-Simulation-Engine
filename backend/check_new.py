import sys
sys.path.insert(0, '.')
errors = []

def try_import(name, stmt):
    try:
        exec(stmt)
        print(f"  OK  {name}")
    except Exception as e:
        print(f"  FAIL {name}: {e}")
        errors.append(name)

print("=== New Module Check ===")
try_import("sentence_transformers", "from sentence_transformers import SentenceTransformer, CrossEncoder")
try_import("rank_bm25", "from rank_bm25 import BM25Okapi")
try_import("chromadb", "import chromadb")
try_import("rag_service", "from app.services.rag_service import get_rag_service")
try_import("rag_agents", "from app.agents.rag_retrieval_agents import ConstitutionRetrievalAgent, LawBookRetrievalAgent, EvidenceRankingAgent, LegalPrincipleAgent, ReasoningAgent, CrossExaminationAgent, ConfidenceAssessmentAgent, FactExtractionAgent, LegalIssueIdentificationAgent")
try_import("report_agent", "from app.agents.report_generation_agent import ReportGenerationAgent")
try_import("orchestrator", "from app.services.orchestrator import LegalReasoningOrchestrator")
try_import("kb_endpoint", "from app.api.endpoints.knowledge_base import router")
try_import("routes", "from app.api.routes import api_router")
try_import("main_app", "from app.main import app")

print(f"\n=== {'ALL OK' if not errors else 'FAILURES: ' + str(errors)} ===")
