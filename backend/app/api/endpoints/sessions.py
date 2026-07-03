"""
Sessions API — user registers LLM provider + API key before uploading cases.
Stored in SQLite (upgrades to PostgreSQL when DATABASE_URL points there).
Admin endpoint lists all sessions with masked keys.
"""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

from app.services.llm_router import get_providers, invoke_llm_sync
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

# In-process cache
_sessions: dict = {}


class SessionCreate(BaseModel):
    provider: str
    api_key: str
    model: str
    user_name: Optional[str] = "Anonymous"
    base_url: Optional[str] = None  # for Ollama


class SessionResponse(BaseModel):
    session_id: str
    provider: str
    model: str
    user_name: str
    created_at: str
    valid: bool
    message: str


@router.get("/providers")
def list_providers():
    return get_providers()


@router.post("/create", response_model=SessionResponse)
async def create_session(body: SessionCreate):
    provider = body.provider.lower().strip()
    if provider not in get_providers():
        raise HTTPException(400, f"Unsupported provider '{provider}'. Choices: {list(get_providers().keys())}")

    # Validate key with a tiny call
    try:
        test = invoke_llm_sync(
            "Reply with just OK",
            provider=provider,
            api_key=body.api_key,
            model=body.model,
            max_tokens=10,
            base_url=body.base_url,
        )
        valid = bool(test)
    except Exception as e:
        raise HTTPException(400, f"API key validation failed: {str(e)}")

    session_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()

    config = {
        "session_id": session_id,
        "provider": provider,
        "api_key": body.api_key,
        "model": body.model,
        "user_name": body.user_name or "Anonymous",
        "base_url": body.base_url or "",
        "created_at": created_at,
        "valid": valid,
        "cases_count": 0,
    }
    _sessions[session_id] = config
    await _db_save(config)
    logger.info(f"Session created {session_id} | {provider}/{body.model} | {body.user_name}")

    return SessionResponse(
        session_id=session_id, provider=provider, model=body.model,
        user_name=config["user_name"], created_at=created_at, valid=valid,
        message=f"✓ API key validated. Using {provider} / {body.model}",
    )


@router.get("/admin/all")
async def admin_list_sessions():
    """Admin view — all sessions with masked keys."""
    rows = await _db_list_all()
    for r in rows:
        k = r.get("api_key", "")
        r["api_key"] = k[:8] + "..." + k[-4:] if len(k) > 12 else "***"
    return {"sessions": rows, "total": len(rows)}


@router.get("/{session_id}")
async def get_session(session_id: str):
    if session_id not in _sessions:
        config = await _db_load(session_id)
        if not config:
            raise HTTPException(404, "Session not found. Please set up your API key first.")
        _sessions[session_id] = config
    c = dict(_sessions[session_id])
    k = c.get("api_key", "")
    c["api_key"] = k[:8] + "..." + k[-4:] if len(k) > 12 else "***"
    return c


def get_session_config_sync(session_id: str) -> dict:
    """Sync getter for orchestrator."""
    return _sessions.get(session_id, {})


# ── DB helpers ────────────────────────────────────────────────────

async def _db_save(config: dict):
    try:
        import aiosqlite, os
        os.makedirs("data", exist_ok=True)
        async with aiosqlite.connect("data/legal_reasoning.db") as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS llm_sessions (
                    session_id TEXT PRIMARY KEY,
                    provider TEXT, api_key TEXT, model TEXT,
                    user_name TEXT, base_url TEXT, created_at TEXT,
                    cases_count INTEGER DEFAULT 0, valid INTEGER DEFAULT 1
                )
            """)
            await db.execute("""
                INSERT OR REPLACE INTO llm_sessions
                (session_id, provider, api_key, model, user_name, base_url, created_at, cases_count, valid)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (config["session_id"], config["provider"], config["api_key"],
                  config["model"], config["user_name"], config.get("base_url", ""),
                  config["created_at"], config.get("cases_count", 0), int(config.get("valid", 1))))
            await db.commit()
    except Exception as e:
        logger.error(f"DB save error: {e}")


async def _db_load(session_id: str) -> dict:
    try:
        import aiosqlite, os
        if not os.path.exists("data/legal_reasoning.db"):
            return {}
        async with aiosqlite.connect("data/legal_reasoning.db") as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM llm_sessions WHERE session_id=?", (session_id,)) as cur:
                row = await cur.fetchone()
                return dict(row) if row else {}
    except Exception as e:
        logger.error(f"DB load error: {e}")
        return {}


async def _db_list_all() -> list:
    try:
        import aiosqlite, os
        if not os.path.exists("data/legal_reasoning.db"):
            return []
        async with aiosqlite.connect("data/legal_reasoning.db") as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM llm_sessions ORDER BY created_at DESC") as cur:
                return [dict(r) for r in await cur.fetchall()]
    except Exception as e:
        logger.error(f"DB list error: {e}")
        return []
