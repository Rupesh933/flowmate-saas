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

===============================================================
# core/dependencies.py
- abhi tk token sirf milta hai, lekin koi route use check nhi karta hai
- so, ham banayenge Protected Route jahan sirf valid token wale hi access kar skte h.

abhi ka scene:
koi bhi /task endpoints bna skta hai
bina login ke bhi kuchh task dekh skta hai (agar bna to)

Hona kya chahiye?
- "Paihle prove karo ki tum login ho (valid token do)
Tabhi task dikhayenge - aur sirf tumare task!

yahi hai [MULTI-TENANCY] ka asli gate!