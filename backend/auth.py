from fastapi import Header, HTTPException

from config import get_settings


def require_api_key(x_api_key: str | None = Header(default=None)) -> str:
    settings = get_settings()
    if not settings.api_key or not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Valid API key required")
    return x_api_key


def require_reviewer(x_api_key: str | None = Header(default=None), x_role: str = Header(default="analyst")) -> str:
    require_api_key(x_api_key)
    if x_role not in {"reviewer", "admin"}:
        raise HTTPException(status_code=403, detail="Reviewer or admin role required")
    return x_role
