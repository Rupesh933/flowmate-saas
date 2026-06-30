# database.py
- PostgreSQL connection - create in one place, all module will be use

# config.py
- read settings from .env - DATABASE_URL, JWT_SECRET etc.

# dependencies.py
- JWT auth check -  get 'current_user', use every protected route

# events.py
- Event Bus - modules 

# redis_client.py
- Redis connection - for cache, blacklist, rate limiting