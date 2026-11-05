
from fastapi import FastAPI, Request, Header, HTTPException, Depends

from app.security.api_key import (
    generate_api_key,
    hash_api_key,
    verify_api_key
)

from app.security.ip_filter import check_ip
from app.security.rate_limiter import rate_limit
from app.security.logger import log_event


app = FastAPI(
    title="Sentinel API",
    description="Secure API Access and Protection System",
    version="1.0.0"
)


# Generate API key
API_KEY = generate_api_key()
API_KEY_HASH = hash_api_key(API_KEY)

print("\n================================")
print("SENTINEL API")
print("Your API Key:", API_KEY)
print("================================\n")


# Security verification
def security_check(
    request: Request,
    x_api_key: str | None = Header(default=None, alias="X-API-Key")
):
    client_ip = request.client.host if request.client else "unknown"

    # 1. Verify API key
    if not x_api_key or not verify_api_key(x_api_key, API_KEY_HASH):
        log_event(f"Invalid or missing API key from {client_ip}")

        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )

    # 2. Verify IP address
    try:
        check_ip(client_ip)
    except HTTPException:
        log_event(f"Blocked IP: {client_ip}")
        raise

    log_event(f"Access granted: {client_ip}")

    return True


# Endpoint 1: Home
@app.get(
    "/",
    dependencies=[Depends(rate_limit())]
)
def home():
    return {
        "project": "Sentinel API",
        "status": "running"
    }


# Endpoint 2: Health
@app.get(
    "/health",
    dependencies=[Depends(rate_limit())]
)
def health():
    return {
        "status": "healthy"
    }


# Endpoint 3: Protected
@app.get(
    "/protected",
    dependencies=[
        Depends(rate_limit()),
        Depends(security_check)
    ]
)
def protected():
    return {
        "message": "Access granted",
        "security": "All checks passed"
    }
