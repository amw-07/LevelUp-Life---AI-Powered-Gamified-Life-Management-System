from fastapi import APIRouter, HTTPException, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    AccessTokenResponse,
)
from app.schemas.user import UserOut
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.services.user_service import get_user_by_email, get_current_user
from app.redis_client import get_redis
from app.config import settings
from jose import JWTError
import redis.asyncio as aioredis

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/register", status_code=201)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    existing = await get_user_by_email(body.email, db)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=body.email,
        username=body.username,
        hashed_password=hash_password(body.password),
        stats={
            "strength": 0, "vitality": 0, "endurance": 0,
            "focus": 0, "efficiency": 0, "execution": 0,
            "intelligence": 0, "creativity": 0, "wisdom": 0,
        },
        goals={"fitness": [], "productivity": [], "learning": []},
        quests_by_domain={"fitness": 0, "productivity": 0, "learning": 0},
        preferred_times={"fitness": "morning", "productivity": "afternoon", "learning": "evening"},
        mindset_profile=[],
    )
    db.add(user)
    try:
        await db.flush()
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Username or email already taken")

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    payload = decode_token(refresh_token)
    jti = payload.get("jti")
    await redis.setex(f"refresh:{jti}", 60 * 60 * 24 * 30, str(user.id))

    response_data = {
        "user": UserOut.model_validate(user),
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

    return response_data


@router.post("/login")
@limiter.limit("5/15minutes")
async def login(
    request: Request,
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    user = await get_user_by_email(body.email, db)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    payload = decode_token(refresh_token)
    jti = payload.get("jti")
    await redis.setex(f"refresh:{jti}", 60 * 60 * 24 * 30, str(user.id))

    response = {
        "user": UserOut.model_validate(user),
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

    if settings.ENVIRONMENT == "production":
        from fastapi.responses import JSONResponse
        import json
        from app.schemas.user import UserOut as _UserOut
        resp = JSONResponse(content={
            "user": json.loads(UserOut.model_validate(user).model_dump_json()),
            "access_token": access_token,
        })
        resp.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=60 * 60 * 24 * 30,
            path="/",
        )
        return resp

    return response


@router.post("/refresh")
async def refresh(
    body: RefreshRequest,
    redis: aioredis.Redis = Depends(get_redis),
):
    try:
        payload = decode_token(body.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        jti = payload.get("jti")
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    stored = await redis.get(f"refresh:{jti}")
    if not stored:
        raise HTTPException(status_code=401, detail="Refresh token expired or revoked")

    new_access = create_access_token(user_id)
    return {"access_token": new_access}


@router.post("/logout")
async def logout(
    body: RefreshRequest | None = None,
    user: User = Depends(get_current_user),
    redis: aioredis.Redis = Depends(get_redis),
):
    if body and body.refresh_token:
        try:
            payload = decode_token(body.refresh_token)
            jti = payload.get("jti")
            if jti:
                await redis.delete(f"refresh:{jti}")
        except Exception:
            pass
    return {"success": True}
