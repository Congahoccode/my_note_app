import os
import requests
from datetime import datetime
from typing import List
from urllib.parse import urlencode

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from firebase_config import db, auth
from models import NoteCreate, NoteUpdate, NoteResponse, LoginRequest

# ─────────────────────────────────────────────
# Load .env
# ─────────────────────────────────────────────
load_dotenv()

FIREBASE_API_KEY     = os.getenv("FIREBASE_API_KEY")
GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
BACKEND_PUBLIC_URL   = os.getenv("BACKEND_PUBLIC_URL")
FRONTEND_URL         = os.getenv("FRONTEND_URL", "http://localhost:8501")

# ─────────────────────────────────────────────
# App setup
# ─────────────────────────────────────────────
app = FastAPI(
    title="MyNoteApp API",
    description="Backend API cho ứng dụng quản lý ghi chú cá nhân",
    version="1.0.0",
)

app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# Auth dependency
# ─────────────────────────────────────────────
async def get_current_user(request: Request) -> str:
    """Xác thực Firebase ID Token, trả về uid."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    try:
        decoded = auth.verify_id_token(auth_header.split(" ")[1])
        return decoded["uid"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ─────────────────────────────────────────────
# General
# ─────────────────────────────────────────────
@app.get("/", tags=["General"])
async def root():
    return {"message": "MyNoteApp Backend is running!"}


@app.get("/health", tags=["General"])
async def health():
    return {"status": "ok"}


# ─────────────────────────────────────────────
# Auth — Email / Password
# ─────────────────────────────────────────────
@app.post("/auth/login", tags=["Auth"])
async def login(body: LoginRequest):
    """Đăng nhập bằng email/password qua Firebase REST API."""
    try:
        r = requests.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}",
            json={"email": body.email, "password": body.password, "returnSecureToken": True},
            timeout=10,
        )
        data = r.json()
        if r.status_code != 200:
            raise HTTPException(status_code=400, detail=data.get("error", {}).get("message", "Login failed"))
        return {"id_token": data["idToken"], "email": data["email"], "expires_in": data["expiresIn"]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")


@app.get("/auth/me", tags=["Auth"])
async def get_me(uid: str = Depends(get_current_user)):
    """Trả về uid của người dùng đang đăng nhập."""
    return {"uid": uid}


# ─────────────────────────────────────────────
# Auth — Google OAuth 2.0
# ─────────────────────────────────────────────
@app.get("/auth/google/login", tags=["Auth"])
async def google_login():
    """Bước 1: Redirect người dùng tới trang chọn tài khoản Google."""
    params = {
        "client_id":     GOOGLE_CLIENT_ID,
        "redirect_uri":  f"{BACKEND_PUBLIC_URL}/auth/google/callback",
        "response_type": "code",
        "scope":         "openid email profile",
        "access_type":   "offline",
        "prompt":        "select_account",
    }
    return RedirectResponse("https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params))


@app.get("/auth/google/callback", tags=["Auth"])
async def google_callback(code: str = None, error: str = None):
    """Bước 2: Nhận code từ Google → đổi lấy Firebase ID token → redirect về Streamlit."""
    redirect_uri  = f"{BACKEND_PUBLIC_URL}/auth/google/callback"
    error_url     = f"{FRONTEND_URL}?google_error="

    if error or not code:
        return RedirectResponse(error_url + "access_denied")

    # Đổi authorization code → Google tokens
    try:
        token_data = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code, "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri, "grant_type": "authorization_code",
            },
            timeout=10,
        ).json()
        if "error" in token_data:
            return RedirectResponse(error_url + "token_exchange_failed")
        google_id_token = token_data.get("id_token")
        access_token    = token_data.get("access_token")
    except Exception:
        return RedirectResponse(error_url + "token_request_failed")

    # Lấy email từ Google userinfo
    try:
        email = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        ).json().get("email", "")
    except Exception:
        return RedirectResponse(error_url + "userinfo_failed")

    # Đổi Google ID token → Firebase ID token
    try:
        firebase_data = requests.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={FIREBASE_API_KEY}",
            json={
                "postBody":            f"id_token={google_id_token}&providerId=google.com",
                "requestUri":          redirect_uri,
                "returnIdpCredential": True,
                "returnSecureToken":   True,
            },
            timeout=10,
        ).json()
        if "error" in firebase_data:
            return RedirectResponse(error_url + "firebase_auth_failed")
    except Exception:
        return RedirectResponse(error_url + "firebase_request_failed")

    # Redirect về Streamlit kèm token và email
    return RedirectResponse(
        f"{FRONTEND_URL}?" + urlencode({"token": firebase_data["idToken"], "email": firebase_data.get("email", email)})
    )


# ─────────────────────────────────────────────
# Notes CRUD
# ─────────────────────────────────────────────
def notes_ref(uid: str):
    return db.collection("users").document(uid).collection("notes")


@app.post("/notes", response_model=NoteResponse, status_code=201, tags=["Notes"])
async def create_note(note: NoteCreate, uid: str = Depends(get_current_user)):
    """Tạo ghi chú mới."""
    now       = datetime.utcnow()
    note_data = {**note.model_dump(), "created_at": now, "updated_at": now}
    doc_ref   = notes_ref(uid).document()
    doc_ref.set(note_data)
    return NoteResponse(id=doc_ref.id, **note_data)


@app.get("/notes", response_model=List[NoteResponse], tags=["Notes"])
async def list_notes(uid: str = Depends(get_current_user)):
    """Lấy danh sách ghi chú, mới nhất lên đầu."""
    docs = notes_ref(uid).order_by("created_at", direction="DESCENDING").stream()
    return [NoteResponse(id=doc.id, **doc.to_dict()) for doc in docs]


@app.get("/notes/{note_id}", response_model=NoteResponse, tags=["Notes"])
async def get_note(note_id: str, uid: str = Depends(get_current_user)):
    """Lấy chi tiết một ghi chú."""
    doc = notes_ref(uid).document(note_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteResponse(id=doc.id, **doc.to_dict())


@app.put("/notes/{note_id}", response_model=NoteResponse, tags=["Notes"])
async def update_note(note_id: str, note: NoteUpdate, uid: str = Depends(get_current_user)):
    """Cập nhật nội dung ghi chú."""
    doc_ref = notes_ref(uid).document(note_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Note not found")
    doc_ref.update({**note.model_dump(), "updated_at": datetime.utcnow()})
    return NoteResponse(id=note_id, **doc_ref.get().to_dict())


@app.delete("/notes/{note_id}", tags=["Notes"])
async def delete_note(note_id: str, uid: str = Depends(get_current_user)):
    """Xóa một ghi chú."""
    doc_ref = notes_ref(uid).document(note_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Note not found")
    doc_ref.delete()
    return {"message": "Note deleted successfully"}
