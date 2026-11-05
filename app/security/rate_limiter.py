from collections import defaultdict, deque
from time import monotonic
from threading import Lock

from fastapi import Request, HTTPException


# Rate-limit configuration
RATE_LIMIT = 10
TIME_WINDOW = 60

# Store request timestamps separately for each client and endpoint
request_history = defaultdict(deque)

# Protect shared data when requests arrive concurrently
rate_limit_lock = Lock()


def rate_limit(limit=RATE_LIMIT, window=TIME_WINDOW):
    """
    Reusable rate-limiting dependency.

    Each client IP gets a separate request counter
    for each API endpoint.
    """

    async def check_rate_limit(request: Request):

        client_ip = (
            request.client.host
            if request.client
            else "unknown"
        )

        endpoint = request.url.path

        # Separate counter for each IP and endpoint
        client_key = (client_ip, endpoint)

        current_time = monotonic()

        with rate_limit_lock:

            timestamps = request_history[client_key]

            # Remove requests outside the time window
            while timestamps and current_time - timestamps[0] >= window:
                timestamps.popleft()

            # Check whether the client exceeded the limit
            if len(timestamps) >= limit:

                retry_after = max(
                    1,
                    int(window - (current_time - timestamps[0]))
                    + 1
                )

                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Maximum {limit} requests per {window} seconds.",
                    headers={"Retry-After": str(retry_after)}
                )

            # Record this request
            timestamps.append(current_time)

    return check_rate_limit