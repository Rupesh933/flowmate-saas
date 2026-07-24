# routes.py
- GET /ai/insights
- POST /ai/schedule
- features of API

# serviecs.py
- call the API, check REdis cache, save the insights


===============================
# modules/ai/models.py

# pattern_type = Column(String, nullable=False)
Yeh batata hai — AI ne KAUN SI CHEEZ
ka pattern dhundha hai!

Possible values (jo hum khud decide karte hain):

"skip_pattern"  → "Tu bahut skip karta hai"
"time_pattern"  → "Tu is time distracted hota hai"
"streak_pattern"→ "Tera streak toot raha hai"

Kyun chahiye?
Agar user ke paas 10 insights hon,
category se filter kar sakte hain:

"Sirf time-related insights dikhao"

# suggestion = Column(String, nullable=False)
Yeh AI ka ACTUAL text message hai!

Example:
"Tu Wednesday ko physics skip karta hai —
 subah 9 baje try kar!"

Yeh string user ko directly dikhega
app mein — jaise ek notification!

# confidence = Column(Float, nullable=False)
AI KITNA SURE HAI is suggestion ke baare mein?

Value hamesha 0.0 se 1.0 ke beech!

confidence = 0.95 → 95% sure! "Bahut strong pattern"
confidence = 0.60 → 60% sure  "Medium pattern"
confidence = 0.30 → 30% sure  "Weak pattern, shayad galat ho"

REAL EXAMPLE:

Priya ne Physics 10 baar skip kiya,
9 baar "distracted" reason diya
→ confidence = 0.90 (bahut strong pattern!)

Priya ne Physics 3 baar skip kiya,
alag alag reasons diye
→ confidence = 0.40 (weak pattern, pakka nahi)

KYUN IMPORTANT HAI:
Agar confidence < 0.5 → Suggestion
mat dikhao user ko (galat ho sakta hai!)

Agar confidence > 0.8 → Confidently
dikhao! "Yeh definitely tumhara pattern hai"

# is_read = Column(Boolean, default=False)
User ne yeh insight DEKHA ya nahi?

Naya insight banta hai → is_read = False
                          (Red dot dikhega app mein!)

User click karke padhe → is_read = True
                          (Red dot hat jayega)

Yeh EXACTLY waisa hai jaise WhatsApp
mein unread messages ka blue tick!

# generated_at = Column(DateTime(timezone=True), server_default=func.now())
Kab yeh insight AI ne banayi?

Kyun chahiye?
"Last week ki insights dikhao"
"Sabse recent insight kya hai?"

Yeh sorting ke kaam aayega!
=============================================================

================================================================
# modules/ai/schemas.py
Normal modules mein:
User CREATE karta hai (POST request)

AI Module mein:
User CREATE nahi karta — AI khud banata hai!

Toh humein sirf yeh chahiye:
1. RESPONSE schema (jo user ko dikhega)

CREATE schema ki zaroorat nahi —
kyunki user khud insight nahi banata,
SERVER (Groq AI) banata hai!

# class Config:
#    from_attributes = True
- response ke liye ye add karna jaruri haib - bina iske database object se response nhi banega
Yaad hai kyun chahiye?

Database se AiInsights object aata hai
(SQLAlchemy object)

Pydantic ko batana padta hai:
"Is object se seedha values utha lo"

Bina Config ke → Error aayega!f

==================================================================

====================================
Bahut saari companies "AI-powered" bolti
hain apne product ko — lekin bahut kam
log ACTUALLY samajh ke implement karte hain!

Tumne khud:
- Groq API integrate ki
- Prompt engineering ki (data ko
  structured prompt mein convert kiya)
- Response ko database mein save kiya
- Multi-tenancy maintain rakhi

Yeh interview mein DEFINITELY
discuss karne wali cheez hai! 💪

=================================================
# AI Response Cache 
- Groq API free tier mein limited requests hain. Agar same user baar baar same type ka insight generate kare, cache se do — Groq API mat bulao

Scenario:

Rahul 10:00 AM ko insight generate kare
→ Groq API call hoti hai (1 call use hui)
→ Result Redis mein cache ho jaaye
   (1 ghante ke liye)

Rahul 10:15 AM ko FIR insight generate kare
→ Cache mein hai! Groq API call NAHI hoti!
→ FREE mein result mil jaata hai!

Rahul 11:30 AM ko insight generate kare
→ Cache EXPIRE ho chuka (1 ghanta beet gaya)
→ Naya Groq API call hoti hai
→ Naya result cache hota hai

# Return type problem

* Problem:
- generate_insight() ek AiInsights
OBJECT return karta hai (database
se)

- Lekin Redis sirf STRINGS store
kar sakta hai!

- Toh agar cache se return karein,
kya PURA object milega?

- NAHI! Sirf STRING (ai_text) milega!

* Solution 
- Option A:
Cache sirf ai_text (suggestion) ko
karo — response mein sirf woh text
bhej do (poora object nahi)

- Option B:
Cache karne se pehle, phir bhi
database mein NAYI entry banao
(chahe Groq API na bhi call ho)
— taaki response format same rahe

User request kare: POST /ai/generate
        ↓
Cache key banao: "ai_insight:{user_id}"
        ↓
Redis mein check karo
        ↓
   MILA?                  NAHI MILA?
     ↓                         ↓
Cached text use karo    Groq API call karo
     ↓                         ↓
DB mein NAYI row banao   Result cache karo (Redis)
(cached text ke saath)         ↓
     ↓                   DB mein NAYI row banao
Return karo                    ↓
                          Return karo