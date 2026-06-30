# routes.py
- API endpoints:
- POST /auth/signup
- POST /auth/login
- POST /auth/logout

# models.py
- python code for USER and SESSIONS database

# schemas.py
- Request/Response validation - email format, password length ect

# services.py
- Bussiness logic - password hash, make JWT, token verify

====================================================================
modules/auth/models.py
class User(Base):
    __tablename__ = "users"
Base (jo humne database.py mein banaya tha) se inherit kiya — yeh batata hai SQLAlchemy ko ki "yeh ek database table hai, naam 'users'".

# id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
UUID kyun, integer (1,2,3) kyun nahi?

Integer:  Easy guess karna — "agla user id 5 hoga"
          Security risk!

UUID:     "a1b2c3d4-e5f6-..." — impossible guess karna
          Production-grade security!

default=uuid.uuid4 → automatically random UUID generate
                      hoga jab naya user banega

# email = Column(String, unique=True, nullable=False, index=True)
unique=True   → Do users same email use nahi kar sakte
nullable=False → Email khali nahi chhod sakte (required!)
index=True    → Email se search FAST hogi (login ke liye
                 baar baar email se dhundhna padta hai)

# created_at = Column(DateTime(timezone=True), server_default=func.now())
server_default=func.now() → PostgreSQL khud current time
                              daal dega jab row banegi

Manual time dene se better — database ka time hamesha
accurate hota hai!
=====================================================================

=====================================================================
# modules/auth/schemas.py
<Why this page?>
User signup karega toh kya bhejega?
{
  "name": "Rahul",
  "email": "rahul@gmail.com",
  "password": "mypassword123"
}

Schema ka kaam:
✅ Check karo email sahi format mein hai ya nahi
✅ Check karo password chhota toh nahi
✅ Galat data aaye toh AUTOMATIC error do

Yeh hota hai Pydantic se — FastAPI ka built-in tool!

# BaseModel
- This is the class of pydantic, By inheriting from it, we define the shape of the data.

# Why password UserCreate and UserResponse is different
SIGNUP REQUEST mein user bhejta hai:
{
  "name": "Rahul",
  "email": "rahul@gmail.com",
  "password": "mypass123"     ← Plain text password!
}

RESPONSE mein hum WAPAS bhejte hain:
{
  "id": "abc-123",
  "name": "Rahul",
  "email": "rahul@gmail.com",
  "plan": "free"
  // password_hash KABHI NAHI bhejte! 🔒
}
* Yeh security ka golden rule hai — password (ya uska hash) kabhi bhi response mein wapas nahi jaana chahiye!

class Config:
    from_attributes = True
- Yeh pydantic ko batata hai ki SQLAlchemy object se directly data le skta hai (eg: user.name, user.email) -- convert karne ki jarurat nhi hoti hai
==================================================================

==================================================================
# modules/auth/services.py
- why services.py?
- Yaad hai humne pehle samjha tha?

routes.py   = Traffic police (sirf request leta hai)
service.py  = Asli kaam karne wala (logic yahan hota hai)

Signup mein services.py kya karega:
- 1. Check karo email paihle se exist to nhi hai
- 2. password ko HASH karo (encrypt)
- 3. Database me new user save karo
- 4. User wapas return karo

# passlib - password hashing algorithm
- install karenge taki password hash kr sake
bcrypt = Password hashing algorithm

Plain password:  "mypassword123"
                       ↓ (bcrypt se hash karo)
Hashed password: "$2b$12$KIXxPfn8Y...xyz"

Yeh ONE-WAY hai — hash se wapas password nikal
NAHI sakte! Sirf compare kar sakte ho:
"Yeh password is hash se match karta hai ya nahi?"

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
- Ek tool banaya ho password hash ya verify karega. isse hum puri file me use karenge
