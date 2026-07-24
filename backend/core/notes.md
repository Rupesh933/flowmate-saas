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

=========================================================


=================================================================

# core/redis_client.py
Socho tum kitchen mein khana bana rahe ho:

FRIDGE (Refrigerator):
  → Bahar rakha hai
  → Cheez nikalne mein 10 second lagte hain
  → Bahut saara saman rakh sakte ho
  → Bijli jaaye toh bhi saman safe rehta hai

KITCHEN COUNTER:
  → Bilkul haath ke paas
  → Cheez uthane mein 1 second lagta hai
  → Thoda hi saman rakh sakte ho
  → Kitchen band karo toh saman hata dete ho

FRIDGE = DATABASE (PostgreSQL)
  → Permanent storage
  → Thoda slow (disk se padhna)
  → Bahut saara data rakh sakta hai

COUNTER = REDIS
  → Temporary storage (RAM mein)
  → Bahut FAST (memory se padhna)
  → Thoda hi data rakhte hain (jo abhi
     chahiye)

## Real definition
Redis = REmote DIctionary Server

Yeh ek "in-memory" database hai
Matlab: Data RAM mein store hota hai
        (Hard disk mein nahi!)

RAM se padhna = Bahut fast! ⚡
Disk se padhna = Thoda slow 🐢

Difference:
PostgreSQL query  → 5-50 milliseconds
Redis query       → 0.1-1 millisecond
                     (50-100x FASTER!)

Redis mein data "KEY-VALUE" pair mein
store hota hai — jaise Python dictionary!

Python mein:
my_dict = {
    "name": "Rahul",
    "age": 25
}
print(my_dict["name"])  # "Rahul"

Redis mein BILKUL WAISA hi:
SET name "Rahul"
GET name  → "Rahul"

------------------------------------------------------------------
| Redis Ke 3 Main Commands
|-- Command 1 — SET (Data Store Karo) --
|  redis_client.set("key_name", "value")
|  # Example:
|  redis_client.set("blacklist:token123", "true")
|
|-- Command 2 — GET (Data Nikaalo) --
|  value = redis_client.get("key_name")
|  # Example:
|  value = redis_client.get("blacklist:token123")
|  # Return: "true" ya None (agar exist nahi karta)
|
|-- Command 3 — SETEX (Time Ke Saath Store Karo!) --
|  redis_client.setex("key_name", seconds, "value")
|  # Example:
|  redis_client.setex("blacklist:token123", 86400, "true")
|  #                                        ^^^^^
|  #                                    24 ghante (seconds mein)
|  SETEX ka Matlab:
|  "Yeh data store karo, LEKIN
|  itne seconds baad KHUD-BA-KHUD
|  DELETE ho jaaye!"
|
|  Yeh REDIS ka SUPERPOWER hai!


# Real Example — JWT Blacklist Kaise Kaam Karega
Scenario: Rahul logout karta hai

Step 1: Uska JWT token blacklist karo
redis_client.setex(
    f"blacklist:{token}",
    86400,  # 24 ghante
    "true"
)

Step 2: Agar Rahul WAHI token use
        karke koi request bheje:

token_check = redis_client.get(f"blacklist:{token}")

if token_check:
    # "true" mila — token BLACKLISTED hai!
    raise HTTPException(401, "Token invalid")

24 ghante baad:
Redis KHUD data delete kar dega!
(Kyunki humne setex mein 86400
 seconds diye the)

Humein MANUALLY delete karne ki
zaroorat nahi! 🎉   

# Real Example — AI Cache Kaise Kaam Karega
Scenario: Rahul AI insight generate
          karta hai

Step 1: Pehle Redis mein check karo
cached = redis_client.get(f"ai:{user_id}")

if cached:
    return cached  # FREE! Groq API
                    # call hi nahi kiya!

Step 2: Agar cache mein NAHI mila:
ai_response = call_groq_api()  # Paisa lagta hai!

# Ab isko 1 ghante ke liye cache karo:
redis_client.setex(
    f"ai:{user_id}",
    3600,  # 1 ghanta (seconds mein)
    ai_response
)

return ai_response

# Faayda:
Agar Rahul 10 baar same question
puche 1 ghante ke andar:

BINA CACHE:
10 baar Groq API call → 10x cost!

WITH CACHE:
1 baar Groq API call (pehli baar)
9 baar Redis se FREE mein milta hai!

# IMPORTANT CONCEPT:

PostgreSQL:
Data hamesha rehta hai (jab tak
delete na karo)

Redis:
Data ya toh:
1. TIME ke saath expire ho jaata hai
   (jaise SETEX mein humne bataya)
2. Container restart hone par
   GAYAB ho sakta hai
   (agar persistence setup na ho)

Isliye Redis ka use SIRF:
✅ Temporary data ke liye
✅ Cache ke liye
✅ Session/token ke liye

❌ IMPORTANT permanent data
   (jaise USER details) Redis
   mein NAHI rakhte — woh
   PostgreSQL mein hi rehta hai!

------------------------------------------------------------------

# Python Mein Redis Kaise Use Karte Hain

1. Install Redis Client
pip install redis


2. Import redis
import redis

3. Create Connection
redis_client = redis.from_url("redis://redis:6379")

4. SET (Store Data)
redis_client.set("name", "Rahul")

5. GET (Retrieve Data)
value = redis_client.get("name")
print(value.decode())  # b'Rahul' → string mein

6. SETEX (Set with Expiry)
redis_client.setex("temp", 60, "data")  # 60 seconds

7. Delete Data
redis_client.delete("name")

------------------------------------------------------------------

# Python Mein Redis JSON Kaise Use Karte Hain
# JSON Data Ko Redis Mein Secure Kaise Rakhte Hain

JSON in Python =
Python dictionaries  {
                       "key": "value"
                     }

Redis JSON Commands:
Command	      Python Method		    Purpose
HSET	  redis_client.hset("key", "field", "value")	  Hash table (field-value pairs)
HGET	  redis_client.hget("key", "field")	          Get specific field
HGETALL	hredis_client.hgetall("key")	          Get all fields
HSETNX	  redis_client.hsetnx("key", "field", "value")	  Set if not exists
HDEL	  redis_client.hdel("key", "field")	          Delete field
HKEYS	  redis_client.hkeys("key")	            Get all keys
HVALS	hredis_client.hvals("key")	            Get all values
HSCAN	  redis_client.hscan_iter("key")	          Iterate over fields
------------------------------------------------------------------

# Real use case of Redis
abhi tak user logout karta hai, kuchh nhi hota! Token tab tak valid rehta hai jabtak khud expire na ho(24 hours)

* Problem 
- Rahul logout karta hai leken uska purana token abhi tak kam karta hai
- Koi bhi jisne token chura liya, 24 ghante tak use kar skta hai, chahe Rahul logout kar chuka ho

* Solution
- Token ko Redis me backlist karo
- Jab bhi koi request aaye us request ke sath - check karo backlisted hai nhi
- Agar backlisted hai -> Reject karo