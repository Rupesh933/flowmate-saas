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

security = HTTPBearer()
- FastAPI ko bata rahe h ki API Authentication ke liye Bearer Token (JWT Token) use karegi.
- security ek object hai jo request ke authorization header se token nikalega
man lo collage me entry karne ke liye ID card chahiye
tab yahan ID card JWT Token ho gaya
or security gard HTTPBearer ho gaya
Guard check karta hai, kya tumare pass valid ID card(token) hai?

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
ye get_db() ke jaise hi kam karta hai
Koi bhi route jo "current logged-in user" chahta hai,
bas yeh likh dega:

def my_route(user: User = Depends(get_current_user)):
    # 'user' automatically mil jaayega!

token = credentials.credentials
payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
user_id: str = payload.get("sub")

Step 1: Token nikalo header se
Step 2: Decode karo — JWT_SECRET se verify hota hai
        ki yeh token GENUINE hai (humne hi banaya tha)
Step 3: payload se user_id nikalo ("sub" field, yaad
        hai humne create_access_token mein daala tha?)

except JWTError:
    raise HTTPException(status_code=401, detail="Invalid ya expired token")
Agar token:
- Galat hai (kisi ne fake banaya)
- Expire ho gaya (24 ghante se zyada purana)
- Corrupt hai

→ Turant 401 error! Aage badhne hi nahi dega.

user = db.query(User).filter(User.id == user_id).first()

if user is None:
    raise HTTPException(...)

return user

Token se mile user_id se ACTUAL user database se
nikalo. (Agar user delete ho gaya ho beech mein,
toh yeh catch karega!)

Sab sahi hai → User object return karo!