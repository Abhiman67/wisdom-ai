"""
FastAPI backend for Wisdom AI (Bhagavad Gita Assistant)

Exposes minimal endpoints used by the new Next.js frontend:
 - GET /health
 - POST /chat { message: string }

Reuses model + RAG logic from gradio_ui.py to avoid duplication.
Run:
  .\.venv\Scripts\python.exe -m uvicorn api_server:app --host 0.0.0.0 --port 8000
"""
from fastapi import FastAPI, Request, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
import re
from typing import Optional, List, Dict, Any
from threading import Thread
from datetime import datetime, timedelta
import random
import time
from fastapi.responses import StreamingResponse
from transformers import TextIteratorStreamer
from sqlalchemy.orm import Session

# Reuse core logic from existing module
import gradio_ui as core

# Database imports
from db import (
    init_db,
    get_db,
    create_query,
    create_response,
    create_retrieval,
    create_error_log,
    log_exception,
    get_query_by_id,
    get_recent_queries,
    get_recent_errors,
    get_db_stats,
)
from db.database import get_db_context

app = FastAPI(title="Wisdom AI Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    temperature: float | None = 0.6
    top_p: float | None = 0.9
    repetition_penalty: float | None = 1.1
    max_new_tokens: int | None = 300
    persona: bool | None = True
    rag: bool | None = True
    rag_k: int | None = 3
    rag_max_chars: int | None = 800


class ChatResponse(BaseModel):
    reply: str
    detected_mood: str
    verse_id: str
    verse_text: str
    verse_source: str


# Local references to model and tokenizer
_tokenizer = None
_model = None
_store: Dict[str, Any] = {
    "users": {},
    "sessions": {},
    "saved_verses": {},
    "collections": {},
    "notifications": {},
    "reading_plans": [],
    "user_plans": {},
    "moderation_queue": [],
    "admin_users": [],
}
_id_counters = {"collection": 1, "note": 1, "comment": 1, "notif": 1, "user": 1}


def _parse_context_meta(ctx: str) -> tuple[str, str, str]:
    """Parse [Chapter X, Verse Y] prefix if present and return (verse_id, verse_text, verse_source)."""
    verse_id = ""
    verse_text = ctx
    verse_source = ""
    m = re.match(r"^\[Chapter\s+(\d+),\s*Verse\s+(\d+)\]\n(.*)$", ctx, flags=re.DOTALL)
    if m:
        chap = m.group(1)
        verse = m.group(2)
        rest = m.group(3).strip()
        verse_id = f"{chap}.{verse}"
        verse_source = f"Bhagavad Gita {chap}.{verse}"
        verse_text = rest
    return verse_id, verse_text, verse_source


def _detect_mood(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["sad", "upset", "depressed", "down"]):
        return "sad"
    if any(k in t for k in ["anxious", "worried", "fear", "afraid"]):
        return "anxious"
    if any(k in t for k in ["angry", "mad", "furious"]):
        return "angry"
    if any(k in t for k in ["peace", "calm", "grateful", "happy", "joy"]):
        return "calm"
    return "neutral"


@app.on_event("startup")
def _startup() -> None:
    global _tokenizer, _model
    
    # Initialize database
    init_db()
    
    device_pref = "cuda" if torch.cuda.is_available() else "cpu"
    # Prepare RAG (optional) similar to gradio_ui.main()
    try:
        try:
            core.load_embedder(device=device_pref)
            try:
                _ = core._rag_embedder.encode(["warmup"], convert_to_tensor=True, device=device_pref)
            except Exception:
                pass
        except Exception as e:
            print(f"(Optional) RAG embedder not available: {e}")
        core.build_or_load_rag_index(device=device_pref)
        print(f"✓ RAG ready on {device_pref}")
    except Exception as e:
        print(f"(Optional) RAG init failed: {e}")

    # Load the model once
    _tokenizer, _model = core.load_model()
    try:
        active = getattr(_model, "active_adapters", None) or getattr(_model, "active_adapter", None)
        peft_keys = list(getattr(_model, "peft_config", {}).keys())
        print("Adapter status -> active_adapters:", active, "| peft_config keys:", peft_keys)
    except Exception:
        pass


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    start_time = time.time()
    query_record = None
    
    # Log query to database
    try:
        with get_db_context() as db:
            query_record = create_query(
                db=db,
                question=req.message,
                temperature=float(req.temperature or 0.6),
                max_tokens=int(req.max_new_tokens or 300),
                rag_enabled=bool(req.rag if req.rag is not None else True),
            )
            query_id = query_record.id
    except Exception as e:
        print(f"Warning: Failed to log query to database: {e}")
        query_id = None
    
    if _model is None or _tokenizer is None:
        return ChatResponse(
            reply="Model is loading, please try again shortly.",
            detected_mood="neutral",
            verse_id="",
            verse_text="",
            verse_source="",
        )

    # Build optional RAG context
    extra_ctx = ""
    first_ctx = ""
    ctx_list = []
    if req.rag:
        try:
            ctx_list = core.retrieve_contexts(
                req.message,
                k=int(req.rag_k or 3),
                max_chars=int(req.rag_max_chars or 800),
                device="cpu",
            )
            if ctx_list:
                first_ctx = ctx_list[0]
                extra_ctx = "\n\n---\n\n".join([f"Context {i+1}:\n{c}" for i, c in enumerate(ctx_list)])
                
                # Log retrievals to database
                if query_id:
                    try:
                        with get_db_context() as db:
                            for i, ctx in enumerate(ctx_list):
                                verse_id, verse_text, verse_source = _parse_context_meta(ctx)
                                create_retrieval(
                                    db=db,
                                    query_id=query_id,
                                    chunk_text=ctx[:500],  # Truncate for storage
                                    rank=i + 1,
                                    source=verse_source or None,
                                )
                    except Exception as e:
                        print(f"Warning: Failed to log retrievals: {e}")
        except Exception as e:
            if query_id:
                try:
                    with get_db_context() as db:
                        log_exception(db, e, query_id=query_id, phase="rag_retrieval")
                except Exception:
                    pass

    try:
        prompt = core.build_prompt(
            req.message,
            context_history=None,
            extra_context=extra_ctx,
            gita_only=bool(req.persona if req.persona is not None else True),
        )

        inputs = _tokenizer(prompt, return_tensors="pt").to(_model.device)
        gen_kwargs = dict(
            max_new_tokens=int(req.max_new_tokens or 300),
            eos_token_id=_tokenizer.eos_token_id,
            pad_token_id=_tokenizer.pad_token_id,
            do_sample=True,
            temperature=float(req.temperature or 0.6),
            top_p=float(req.top_p or 0.9),
            repetition_penalty=float(req.repetition_penalty or 1.1),
        )
        with torch.no_grad():
            out = _model.generate(**inputs, **gen_kwargs)
        text = _tokenizer.decode(out[0], skip_special_tokens=True)
        reply = core.clean_output(text)

        verse_id, verse_text, verse_source = ("", "", "")
        if first_ctx:
            verse_id, verse_text, verse_source = _parse_context_meta(first_ctx)

        detected_mood = _detect_mood(req.message)
        
        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Log response to database
        if query_id:
            try:
                with get_db_context() as db:
                    create_response(
                        db=db,
                        query_id=query_id,
                        answer=reply,
                        latency_ms=latency_ms,
                        tokens_generated=len(out[0]) - len(inputs.input_ids[0]),
                        detected_mood=detected_mood,
                        verse_id=verse_id or None,
                        verse_text=verse_text[:500] if verse_text else None,
                        verse_source=verse_source or None,
                    )
            except Exception as e:
                print(f"Warning: Failed to log response: {e}")

        return ChatResponse(
            reply=reply,
            detected_mood=detected_mood,
            verse_id=verse_id,
            verse_text=verse_text,
            verse_source=verse_source,
        )
    except Exception as e:
        # Log error to database
        if query_id:
            try:
                with get_db_context() as db:
                    log_exception(db, e, query_id=query_id, phase="model_generation")
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=str(e))


# -----------------
# Streaming via SSE
# -----------------
def _sse_format(data: str) -> str:
    return f"data: {data}\n\n"


@app.post("/chat/stream")
def chat_stream(req: ChatRequest):
    if _model is None or _tokenizer is None:
        def gen_loading():
            yield _sse_format("{\"status\":\"loading\"}")
        return StreamingResponse(gen_loading(), media_type="text/event-stream")

    # Prepare RAG context
    extra_ctx = ""
    if req.rag:
        try:
            ctx_list = core.retrieve_contexts(
                req.message,
                k=int(req.rag_k or 3),
                max_chars=int(req.rag_max_chars or 800),
                device="cpu",
            )
            if ctx_list:
                extra_ctx = "\n\n---\n\n".join([f"Context {i+1}:\n{c}" for i, c in enumerate(ctx_list)])
        except Exception:
            pass

    prompt = core.build_prompt(
        req.message,
        context_history=None,
        extra_context=extra_ctx,
        gita_only=bool(req.persona if req.persona is not None else True),
    )

    inputs = _tokenizer(prompt, return_tensors="pt").to(_model.device)
    streamer = TextIteratorStreamer(_tokenizer, skip_special_tokens=True, skip_prompt=True)
    gen_kwargs = dict(
        **inputs,
        max_new_tokens=int(req.max_new_tokens or 300),
        eos_token_id=_tokenizer.eos_token_id,
        pad_token_id=_tokenizer.pad_token_id,
        do_sample=True,
        temperature=float(req.temperature or 0.6),
        top_p=float(req.top_p or 0.9),
        repetition_penalty=float(req.repetition_penalty or 1.1),
        streamer=streamer,
    )

    def generate():
        thread = Thread(target=_model.generate, kwargs=gen_kwargs)
        thread.start()
        partial = ""
        for token in streamer:
            partial += token
            # Clean on the fly by including prompt+partial, then subtract prompt prefix in clean_output
            cleaned = core.clean_output(prompt + partial)
            yield _sse_format(core.json.dumps({"delta": cleaned})) if hasattr(core, "json") else _sse_format(cleaned)
        # Signal end
        yield _sse_format("[DONE]")

    return StreamingResponse(generate(), media_type="text/event-stream")


# -------------------------
# Utility: mock data seeds
# -------------------------
def _seed_data_once():
    if _store.get("_seeded"):
        return
    _store["_seeded"] = True
    # Admin users
    _store["admin_users"] = [
        {
            "id": 1,
            "uuid": "u-1",
            "name": "Admin",
            "email": "admin@example.com",
            "is_admin": True,
            "created_at": datetime.utcnow().isoformat(),
            "last_mood": "calm",
        }
    ]
    # Reading plans
    _store["reading_plans"] = [
        {"id": 1, "name": "Essence of Karma Yoga", "description": "Core verses on action.", "duration_days": 14},
        {"id": 2, "name": "Bhakti Path", "description": "Devotion and surrender.", "duration_days": 10},
    ]
    # Notifications store for user-1
    _store["notifications"]["user-1"] = [
        {"id": 1, "title": "Welcome", "message": "Welcome to Wisdom AI!", "type": "info", "is_read": False, "created_at": datetime.utcnow().isoformat()},
    ]
    # Collections
    _store["collections"][1] = {
        "id": 1,
        "name": "Favorites",
        "description": "My saved gems",
        "verse_count": 1,
        "is_public": False,
        "created_at": datetime.utcnow().isoformat(),
        "verses": [
            {"verse_id": "2.47", "text": "Karmanye vadhikaraste...", "source": "Bhagavad Gita 2.47"}
        ],
    }


# -------------------------
# Auth/session (minimal)
# -------------------------
class LoginRequest(BaseModel):
    email: str
    password: str
    remember: Optional[bool] = False


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: str


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


@app.post("/signup", response_model=TokenResponse)
def signup(req: SignupRequest):
    _seed_data_once()
    # Very simple in-memory user creation; if existing, return token as login would
    existing_user = next((uid for uid, u in _store["users"].items() if u.get("email") == req.email), None)
    if existing_user is None:
        user_id = f"user-{len(_store['users'])+1}"
        _store["users"][user_id] = {
            "user_id": user_id,
            "name": req.name,
            "email": req.email,
            "saved_verses": [],
            "chat_history": [],
            "recent_verses": {},
            "created_at": datetime.utcnow().isoformat(),
        }
    else:
        user_id = existing_user
    token = f"dev-token-{user_id}"
    _store["sessions"][token] = {"user_id": user_id, "created_at": datetime.utcnow().isoformat()}
    return TokenResponse(access_token=token, user_id=user_id, name=_store["users"][user_id].get("name", req.name))


@app.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    _seed_data_once()
    # If user exists, use; else create a basic one
    existing_user = next((uid for uid, u in _store["users"].items() if u.get("email") == req.email), None)
    if existing_user is None:
        user_id = "user-1" if not _store["users"] else f"user-{len(_store['users'])+1}"
        _store["users"][user_id] = {
            "user_id": user_id,
            "name": "Arjun" if user_id == "user-1" else f"User {len(_store['users'])}",
            "email": req.email,
            "saved_verses": ["2.47"] if user_id == "user-1" else [],
            "chat_history": [],
            "recent_verses": {},
        }
    else:
        user_id = existing_user
    token = f"dev-token-{user_id}"
    _store["sessions"][token] = {"user_id": user_id, "created_at": datetime.utcnow().isoformat()}
    name = _store["users"][user_id].get("name", "Arjun")
    return TokenResponse(access_token=token, user_id=user_id, name=name)


@app.post("/logout")
def logout():
    return {"ok": True}


@app.get("/last-session")
def last_session():
    # Minimal placeholder
    return {"ok": True, "timestamp": datetime.utcnow().isoformat()}


# -------------------------
# Profile & Saved verses
# -------------------------
@app.get("/profile")
def profile():
    _seed_data_once()
    u = _store["users"].get("user-1")
    if not u:
        u = {"user_id": "user-1", "name": "Arjun", "email": "arjun@example.com", "saved_verses": [], "chat_history": [], "recent_verses": {}}
    return {
        "user_id": u["user_id"],
        "name": u.get("name", "Arjun"),
        "email": u.get("email", "arjun@example.com"),
        "last_mood": "calm",
        "recent_verses": {"today": ["2.47"]},
        "saved_verses": u.get("saved_verses", []),
        "chat_history": u.get("chat_history", []),
        "created_at": datetime.utcnow().isoformat(),
        "streak": 3,
        "favorite_source": "Bhagavad Gita",
    }


@app.get("/daily-verse-with-save")
def daily_verse_with_save():
    choices = [
        ("2.47", "You have the right to work, but not to the fruits...", "Bhagavad Gita 2.47"),
        ("4.7", "Whenever dharma declines...", "Bhagavad Gita 4.7"),
        ("12.15", "He by whom no one is put into difficulty...", "Bhagavad Gita 12.15"),
    ]
    verse_id, text, source = random.choice(choices)
    is_saved = verse_id in _store["users"].get("user-1", {}).get("saved_verses", [])
    return {"verse_id": verse_id, "text": text, "source": source, "audio_url": None, "image_url": None, "is_saved": is_saved}


@app.post("/save-verse-from-daily")
def save_verse_from_daily():
    _store["users"].setdefault("user-1", {}).setdefault("saved_verses", []).append("2.47")
    return {"ok": True}


@app.get("/my-saved-verses")
def my_saved_verses():
    verses = [
        {"verse_id": "2.47", "text": "You have the right to work...", "source": "Bhagavad Gita 2.47", "image_url": "", "audio_url": ""}
    ]
    return {"saved_verses": verses}


# -------------------------
# Collections
# -------------------------
class CollectionIn(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: Optional[bool] = False


@app.get("/collections")
def list_collections():
    _seed_data_once()
    rows = []
    for c in _store["collections"].values():
        rows.append({k: c[k] for k in ["id", "name", "description", "verse_count", "is_public", "created_at"]})
    return rows


@app.post("/collections")
def create_collection(body: CollectionIn):
    cid = _id_counters["collection"]
    _id_counters["collection"] += 1
    _store["collections"][cid] = {
        "id": cid,
        "name": body.name,
        "description": body.description or "",
        "verse_count": 0,
        "is_public": bool(body.is_public),
        "created_at": datetime.utcnow().isoformat(),
        "verses": [],
    }
    return {"id": cid}


@app.get("/collections/{cid}")
def get_collection(cid: int):
    c = _store["collections"].get(cid)
    if not c:
        return {"detail": "Not found"}
    return c


# -------------------------
# Notifications
# -------------------------
@app.get("/notifications")
def list_notifications(unread_only: Optional[bool] = False):
    _seed_data_once()
    items = _store["notifications"].get("user-1", [])
    if unread_only:
        items = [n for n in items if not n.get("is_read")]
    return items


@app.post("/notifications/{nid}/read")
def read_notification(nid: int):
    items = _store["notifications"].get("user-1", [])
    for n in items:
        if n.get("id") == nid:
            n["is_read"] = True
    return {"ok": True}


# -------------------------
# Reading plans
# -------------------------
@app.get("/reading-plans")
def reading_plans():
    _seed_data_once()
    return _store["reading_plans"]


@app.get("/my-reading-plans")
def my_reading_plans():
    _seed_data_once()
    return _store["user_plans"].get("user-1", [])


@app.post("/reading-plans/{pid}/enroll")
def enroll_plan(pid: int):
    _seed_data_once()
    plans = _store["user_plans"].setdefault("user-1", [])
    if any(p.get("plan_id") == pid for p in plans):
        return {"ok": True}
    plan = next((p for p in _store["reading_plans"] if p["id"] == pid), None)
    if plan:
        plans.append({
            "enrollment_id": len(plans) + 1,
            "plan_name": plan["name"],
            "plan_description": plan["description"],
            "duration_days": plan["duration_days"],
            "current_day": 1,
            "completed": False,
            "start_date": datetime.utcnow().date().isoformat(),
        })
    return {"ok": True}


# Reading plans - admin CRUD and progress updates
class ReadingPlanIn(BaseModel):
    name: str
    description: Optional[str] = None
    duration_days: Optional[int] = 7


@app.post("/reading-plans")
def create_reading_plan(body: ReadingPlanIn):
    _seed_data_once()
    nid = max((p.get("id", 0) for p in _store.get("reading_plans", [])), default=0) + 1
    plan = {"id": nid, "name": body.name, "description": body.description or "", "duration_days": int(body.duration_days), "verses": []}
    _store.setdefault("reading_plans", []).append(plan)
    return {"id": nid}


@app.put("/reading-plans/{pid}")
def update_reading_plan(pid: int, body: ReadingPlanIn):
    _seed_data_once()
    plan = next((p for p in _store.get("reading_plans", []) if p.get("id") == pid), None)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    plan["name"] = body.name
    plan["description"] = body.description or plan.get("description", "")
    plan["duration_days"] = int(body.duration_days)
    return {"ok": True}


@app.delete("/reading-plans/{pid}")
def delete_reading_plan(pid: int):
    _seed_data_once()
    plans = _store.get("reading_plans", [])
    new_plans = [p for p in plans if p.get("id") != pid]
    _store["reading_plans"] = new_plans
    return {"ok": True}


@app.post("/reading-plans/{pid}/progress")
def advance_plan_progress(pid: int, increment: Optional[int] = 1):
    _seed_data_once()
    user_plans = _store.setdefault("user_plans", {}).setdefault("user-1", [])
    p = next((x for x in user_plans if x.get("plan_id") == pid or x.get("enrollment_id") == pid), None)
    if not p:
        # try matching by plan id
        p = next((x for x in user_plans if x.get("plan_name") and x.get("plan_name") == next((q.get("name") for q in _store.get("reading_plans", []) if q.get("id") == pid), None)), None)
    if not p:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    p["current_day"] = min(p.get("duration_days", 1), p.get("current_day", 1) + int(increment))
    if p["current_day"] >= p.get("duration_days", 1):
        p["completed"] = True
    return {"ok": True, "current_day": p["current_day"], "completed": p.get("completed", False)}


# -------------------------
# Admin endpoints
# -------------------------
@app.get("/admin/analytics")
def admin_analytics():
    today = datetime.utcnow().date()
    dau = { (today - timedelta(days=i)).isoformat(): random.randint(5, 25) for i in range(7) }
    events = {k: random.randint(10, 50) for k in ["chat", "save_verse", "login", "share"]}
    return {"event_counts": events, "daily_active_users": dau, "total_events": sum(events.values())}


@app.get("/admin/analytics/engagement")
def admin_engagement(start: Optional[str] = None, end: Optional[str] = None):
    today = datetime.utcnow().date()
    dau = { (today - timedelta(days=i)).isoformat(): random.randint(5, 25) for i in range(14) }
    events = {k: random.randint(10, 50) for k in ["chat", "save_verse", "login", "share"]}
    return {"event_counts": events, "daily_active_users": dau, "total_events": sum(events.values())}


@app.get("/admin/analytics/verse-popularity")
def admin_verse_popularity(limit: int = 10):
    items = [
        {"verse_id": "2.47", "views": random.randint(10, 100), "text": "You have the right to work...", "source": "Bhagavad Gita 2.47"},
        {"verse_id": "4.7", "views": random.randint(10, 100), "text": "Whenever dharma declines...", "source": "Bhagavad Gita 4.7"},
    ]
    return items[:limit]


@app.get("/admin/system-health")
def admin_system_health():
    return {"gpu": torch.cuda.is_available(), "rag_ready": core._rag_built, "model_loaded": _model is not None}


@app.get("/admin/recent-activity")
def admin_recent_activity():
    return [
        {"id": 1, "event": "chat", "user_id": "user-1", "timestamp": datetime.utcnow().isoformat(), "summary": "Asked about 2.47"}
    ]


@app.get("/admin/moderation/flagged")
def admin_flagged():
    return [
        {"id": 1, "verse_id": "2.47", "comment": "Spam", "user_name": "Foo", "user_email": "foo@example.com", "created_at": datetime.utcnow().isoformat()}
    ]


@app.post("/admin/moderation/{cid}/approve")
def admin_approve(cid: int):
    return {"ok": True}


@app.post("/admin/moderation/{cid}/delete")
def admin_delete(cid: int):
    return {"ok": True}


# -------------------------
# Admin DB endpoints (chat history)
# -------------------------
@app.get("/admin/db/stats")
def admin_db_stats():
    """Get database statistics."""
    try:
        with get_db_context() as db:
            stats = get_db_stats(db)
            return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/db/queries")
def admin_db_queries(limit: int = 10, offset: int = 0):
    """Get recent queries with their responses."""
    try:
        with get_db_context() as db:
            queries = get_recent_queries(db, limit=limit, offset=offset)
            result = []
            for q in queries:
                query_dict = q.to_dict()
                # Include response if exists
                if q.response:
                    query_dict["response"] = q.response.to_dict()
                else:
                    query_dict["response"] = None
                result.append(query_dict)
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/db/queries/{query_id}")
def admin_db_query_detail(query_id: int):
    """Get a single query with its response and retrievals."""
    try:
        with get_db_context() as db:
            query = get_query_by_id(db, query_id)
            if not query:
                raise HTTPException(status_code=404, detail="Query not found")
            
            result = query.to_dict()
            result["response"] = query.response.to_dict() if query.response else None
            result["retrievals"] = [r.to_dict() for r in query.retrievals]
            result["errors"] = [e.to_dict() for e in query.errors]
            return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/db/errors")
def admin_db_errors(limit: int = 10, offset: int = 0):
    """Get recent errors."""
    try:
        with get_db_context() as db:
            errors = get_recent_errors(db, limit=limit, offset=offset)
            return [e.to_dict() for e in errors]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/users")
def admin_users():
    _seed_data_once()
    return _store["admin_users"]


# -------------------------
# Admin user management (CRUD)
# -------------------------
class AdminUserIn(BaseModel):
    name: str
    email: str
    is_admin: Optional[bool] = False


@app.post("/admin/users")
def admin_create_user(body: AdminUserIn):
    _seed_data_once()
    nid = max((u.get("id", 0) for u in _store.get("admin_users", []) if isinstance(u.get("id"), int)), default=0) + 1
    user = {
        "id": nid,
        "uuid": f"u-{nid}",
        "name": body.name,
        "email": body.email,
        "is_admin": bool(body.is_admin),
        "created_at": datetime.utcnow().isoformat(),
    }
    _store.setdefault("admin_users", []).append(user)
    return {"id": nid}


@app.put("/admin/users/{uid}")
def admin_update_user(uid: int, body: AdminUserIn):
    _seed_data_once()
    users = _store.get("admin_users", [])
    u = next((x for x in users if x.get("id") == uid), None)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    u["name"] = body.name
    u["email"] = body.email
    u["is_admin"] = bool(body.is_admin)
    return {"ok": True}


@app.delete("/admin/users/{uid}")
def admin_delete_user(uid: int):
    _seed_data_once()
    users = _store.get("admin_users", [])
    _store["admin_users"] = [x for x in users if x.get("id") != uid]
    return {"ok": True}


# -------------------------
# Profile update
# -------------------------
class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


@app.post("/profile")
def profile_update(body: ProfileUpdate = Body(...)):
    _seed_data_once()
    u = _store.setdefault("users", {}).setdefault("user-1", {"user_id": "user-1", "name": "Arjun", "email": "arjun@example.com"})
    if body.name:
        u["name"] = body.name
    if body.preferences:
        u.setdefault("preferences", {}).update(body.preferences)
    return {"ok": True, "user": {"user_id": u.get("user_id"), "name": u.get("name"), "preferences": u.get("preferences", {})}}
