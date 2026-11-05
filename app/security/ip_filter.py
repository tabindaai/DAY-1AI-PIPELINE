from fastapi import HTTPException
from app.config import ALLOWED_IPS

def check_ip(client_ip):

    if client_ip not in ALLOWED_IPS:
        raise HTTPException(
            status_code=403,
            detail="IP address not allowed"
        )

    return True