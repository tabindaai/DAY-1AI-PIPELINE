from fastapi import FastAPI, Request, Header, HTTPException

from app.security.api_key import (
    generate_api_key,
    hash_api_key,
    verify_api_key
)

from app.security.ip_filter import check_ip
from app.security.rate_limiter import check_rate_limit
from app.security.logger import log_event

app = FastAPI(
    title="Sentinel API",
    description="Secure API Access and Protection System",
    version="1.0.0"
)

# Generate an API key for demonstration
API_KEY = generate_api_key()
API_KEY_HASH = hash_api_key(API_KEY)

print("\n================================")
print("SENTINEL API")
print("Your API Key:", API_KEY)
print("================================\n")


# Security verification
def security_check(
    request: Request,
    x_api_key: str = Header(alias="X-API-Key")
):

    client_ip = request.client.host

    # 1. Verify API key
    if not verify_api_key(x_api_key, API_KEY_HASH):
        log_event(f"Invalid API key from {client_ip}")

        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    # 2. Verify IP address
    try:
        check_ip(client_ip)
    except HTTPException:
        log_event(f"Blocked IP: {client_ip}")
        raise

    # 3. Check rate limit
    try:
        check_rate_limit(API_KEY_HASH)
    except HTTPException:
        log_event(f"Rate limit exceeded: {client_ip}")
        raise

    log_event(f"Access granted: {client_ip}")

    return True


# Public endpoint
@app.get("/")
def home():

    return {
        "project": "Sentinel API",
        "status": "running"
    }


# Protected endpoint
@app.get("/protected")
def protected(
    authorized: bool = __import__(
        "fastapi"
    ).Depends(security_check)
):

    return {
        "message": "Access granted",
        "security": "All checks passed"
    }


# Health endpoint
@app.get("/health")
def health():

    return {
        "status": "healthy"
    }