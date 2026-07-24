import os
import redis

# Create Redis client - one time, and use many time
redis_client = redis.from_url(
    os.getenv("REDIS_URL"),
    decode_responses=True  # automatically converts bytes to strings
    # Bina iske → bytes milte hain: b'value'
    # Iske saath → clean string milti hai: 'value'
)   