"""Authentication: JWT issuance, password hashing, dependency to get current user.

Supports two flows:
- Email/password: hashed with bcrypt, JWT issued by us (HS256)
- Google (Emergent): session token validated via Emergent's session API; we issue our own JWT
"""
import os
import time
from datetime import datetime, timezone, timedelta
from typing import Optional

import bcrypt
import jwt
import httpx
from fastapi import Depends, HTTPException, Header, status
from pydantic import BaseModel

from .db import get_sb

JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
JWT_EXP_SECONDS = 60 * 60 * 24 * 30  # 30 days

EMERGENT_SESSION_API = "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data"


class CurrentUser(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    google_sub: Optional[str] = None


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def issue_jwt(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "iat": int(time.time()),
        "exp": int(time.time()) + JWT_EXP_SECONDS,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


async def fetch_emergent_session(session_id: str) -> dict:
    """Fetch user data from Emergent's session-based Google auth."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            EMERGENT_SESSION_API,
            headers={"X-Session-ID": session_id},
        )
        if r.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid Emergent session")
        return r.json()


async def get_current_user(authorization: Optional[str] = Header(None)) -> CurrentUser:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_jwt(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing sub")

    sb = get_sb()
    res = sb.table("app_users").select("id,email,full_name,avatar_url,google_sub").eq("id", user_id).limit(1).execute()
    if not res.data:
        raise HTTPException(status_code=401, detail="User not found")
    u = res.data[0]
    return CurrentUser(
        id=u["id"],
        email=u["email"],
        full_name=u.get("full_name"),
        avatar_url=u.get("avatar_url"),
        google_sub=u.get("google_sub"),
    )
