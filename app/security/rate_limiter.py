import time
from collections import defaultdict, deque
from fastapi import HTTPException

from app.config import RATE_LIMIT, TIME_WINDOW

requests = defaultdict(deque)

def check_rate_limit(client_id):

    current_time = time.time()

    client_requests = requests[client_id]

    while client_requests and current_time - client_requests[0] >= TIME_WINDOW:
        client_requests.popleft()

    if len(client_requests) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded"
        )

    client_requests.append(current_time)