from collections import defaultdict, deque
from time import monotonic
from threading import Lock
from app.security.prime_checker import is_prime
from fastapi import Request, HTTPException


MAX_REQUESTS = 100
TIME_WINDOW = 60

# Store request timestamps separately for each client and endpoint
request_history = defaultdict(deque)

# Protect shared data when requests arrive concurrently
rate_limit_lock = Lock()


def rate_limit( window=TIME_WINDOW):
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

            timestamps.append(current_time)
            request_count = len(timestamps) 

            print("Request count:", request_count)
            print("Is prime:", is_prime(request_count))


            if request_count > MAX_REQUESTS:
                raise HTTPException(
                    status_code=429,
                    detail="Maximum request limit of 100 reached."
                )
            # Check whether the client exceeded the limit
          
            

            if not is_prime(request_count):
             raise HTTPException(
                 status_code=403,
                 detail=f"Request rejected."
                            )
    return check_rate_limit