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

# existing_user = db.query(User).filter(User.email == user_data.email).first()
if existing_user:
    raise HTTPException(...)
db.query(User)   --> User table me dhundo
filter(User.email == user_data.email)  --> Where email = 'rupesh@gmail.com'
first()  -> paihla match do (ya None)

Agar already exist karta hai → Error throw karo!
Same email se 2 accounts nahi ban sakte (UNIQUE constraint
bhi hai, lekin yeh check pehle hi friendly error deta hai)

# hashed_password = pwd_context.hash(user_data.password)
Input:  "mypassword123"
Output: "$2b$12$xK9.../randomstring..."

Yeh asli password kahin store NAHI hota — sirf hash!


# new_user = User(
    name=user_data.name,
    email=user_data.email,
    password_hash=hashed_password,
)
User class jo models.py me banai thi. yahan uska ek object bna rahe h. 
ye ek future database row hai (abhi tak sirf python memory me hai)

db.add(new_user)     # "Yeh row add karne ki taiyari karo"
db.commit()           # "Ab actually save kar do database mein!"
db.refresh(new_user)  # "Database se latest data wapas le aao"

# Why refresh()?

new_user banate time uska 'id' nahi pata (database
generate karega) aur 'created_at' bhi nahi pata.

db.commit() ke baad database ne yeh values generate
kar di hain — refresh() unhe Python object mein wapas
le aata hai!

==========================================================

===============================================================
# modules/auth/routes.py

routes.py ka kam? --> Traffic police

1. Url define karo --> POST /auth/signup
2. Request data lo (schema se validate ho jata hai)
3. service.py ko bolo ye kam karo
4. Response wapas bhejo

Yeh khud koi "heavy" kaam nahi karta — sirf
service.py ko forward karta hai!

# router = APIRouter(prefix='/auth', tags=['Authentication'])
- prefix='/auth'
  --> is router ke sare endpoints '/auth' se suru honge.
      to signup actually bn jaiye '/auth/signup'
- tags=['Authentication']
  ---> '/docs' page pe ye endpoint 'Authentication' group ke andar dikhenge (organized!)

@router.post('/signup', response_model=UserResponse)  
--> POST request handle karega
--> response_model=UserResponse --> FastAPI automatically ensure karega ki resonse UserResponse schema follow kare (password hash hide ho jayega khud hi)

def signup(user_data: UserCreate, db: Session = Depends(get_db)):
- user_data: UserCreate
  request body automatically UserCreate schema se validate hoga

db: Session = Depends(get_db)
- database.py me get_db() banaye the, get_db() yahan use ho raha hai, jisse automatic db session milega

Session ka mtlb :- Session ka matlab hai ek temporary database conversation jisme aap data read, insert, update, ya delete karte ho.

# new_user = services.create_user(db, user_data)
# return new_user
Bas itna! services.py ko bola "yeh kaam karo"
Service ne sab logic kiya (check, hash, save)
Yahan sirf result wapas bhej rahe 


==========================================================================================
# JWT token
ab login banate h! signup ke bad user ko login karna chahiye or ek token milna chahiye jisse main hi hu prove kar ske

JWT kya hota hai?
- Socho ek concert me gaye ho
Entry pr ticker check hoti hai --> Hath pe stump lagta hai
fir jab bhi andar jana ho --> sirf stump dikho ticket dubara nhi dikhani padti hai

JWT token = whi stump ke jaise kam karta hai
- Login -> time token milta hai
- Future request -> Sirf token bhejo password nhi!

JWT ke liye 
pip install python-jose[cryptography]

# JWT_SECRET = os.getenv("JWT_SECRET")
- .env me hamne JWT_SECRET likha tha, o JWT_SECRET yahan use ho raha hai 
- isi se token sign/verify hota hai
! <and this token is not shareable to anyone>

# def authenticate_user(db: Session, login_data: LoginRequest) -> User:
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user or not pwd_context.verify(login_data.password, user.password_hash):
        raise HTTPException(...)

    return user
1. Email se user dhund rahe h
2. pwd_context.verify(plain_password, hashed_password)
- ye check karta hai plain_password, hashed_password se match karta hai ya nhi
- ye True/False return karta hai
3. agar User nhi mila ya password galat hai
- dono cases me same hi error aayega ki 'email or password is wrong'
4. (Security best practice — agar hum bolein "email nahi
 mila" vs "password galat" alag alag, toh hackers ko
 pata chal jaata email exist karta hai ya nahi!)

# def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

1. payload -> Token ke andar kya data hoga
    "sub" --> Kiska token hai (user ka ID)
    "exp" --> kab expire hoga (30min, 1ghante, 24ghante......)
2. jwt.encode()  --> ye sab data ko ek lambi encrypted string me convert kar deta hai, JWT_SECRET se sign karta hai
3. result kuchh aise dikhega  ---> eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJh...

@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user
Depends(get_current_user) → Yeh route AB PROTECTED hai!

Agar koi bina token ke aaye → 401 Unauthorized
Agar valid token ho → current_user mein woh insaan
                       milega jiska token hai

Yeh /me endpoint sabse common pattern hai SaaS
apps mein — "mera profile dikhao" (jaise Facebook
ka "/me" API)