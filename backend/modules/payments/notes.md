# routes.py
- POST /payments/webhook - Rozorpay payment confirm

PAYMENTS (Razorpay)
  → Free/Pro subscription plans
  → Payment webhook handling
  → Plan upgrade logic

Yeh thoda alag hai — kyunki isme third-party service (Razorpay) involve hai, aur webhooks ka naya concept aayega.


Razorpay = India ka payment gateway
           (jaise Stripe, PayPal —
            lekin India ke liye
            optimized)

Kya karta hai?
User "Pro Plan" kharidna chahta hai
     ↓
Razorpay payment page kholta hai
(Card/UPI/Netbanking)
     ↓
Payment successful/failed
     ↓
Razorpay HUMEIN batata hai
(webhook ke through)
     ↓
Hum user ka plan "pro" kar dete hain

# Webhook Kya Hota Hai
Normal API Call (jo humne abhi tak
kiya hai):

User → Humein request bhejta hai
Hum → Response dete hain
(User HUMESHA pehle request karta hai)

WEBHOOK (Naya concept!):

Razorpay → HUMEIN request bhejta hai!
Hum → Response dete hain
(RAZORPAY pehle request karta hai,
 hum nahi!)

# Eg: 
Normal API = Tum Swiggy app khologe
             aur order karoge
             (TUM pehle action lete ho)

Webhook = Swiggy ka delivery boy
          tumhare ghar KHUD aata hai
          jab khana ready ho jaata hai
          (SWIGGY pehle action leta hai,
           tum nahi!)

Payment webhook:
Razorpay: "Payment successful ho gaya!"
   → Yeh HUMARE server ko khud call
     karta hai, batane ke liye! 

# Complete flow
Step 1: User "Upgrade to Pro" click kare

Step 2: Hum Razorpay se ek "Order" banate hain
        (Backend se — Razorpay API call)

Step 3: Razorpay order ID + payment link
        milta hai, hum FRONTEND ko bhejte
        hain

Step 4: User Razorpay ke payment page pe
        jaake Card/UPI se payment kare

Step 5: Payment successful hone par,
        RAZORPAY hume WEBHOOK bhejta hai:
        "Payment ID xyz successful ho gaya!"

Step 6: Hum apna DATABASE update karte hain:
        SUBSCRIPTIONS table mein entry
        USERS.plan = "pro" kar dete hain

# amount_paise kyu..?
Razorpay HAMESHA paise mein amount
leta hai, rupees mein NAHI!

Kyun?
Decimal numbers mein ERROR ho sakti
hai floating point ki wajah se!

Example:
₹499 = 49900 paise

Agar hum "499.00" (float) store karein
→ Computer mein precision issues aa
  sakte hain (499.000001 jaisa kuch!)

Integer mein paise store karna =
SAFE aur ACCURATE!

# expires_at kyu..?
Free plan:
  → Kabhi expire nahi hota
  → expires_at = NULL

Pro plan:
  → 1 mahine baad expire hota hai
  → expires_at = "2024-02-15"

Isiliye nullable=True rakhenge!


# modules/payments/schemas.py
User khud SUBSCRIPTIONS ya PAYMENT_LOGS
create NAHI karta!

Yeh SERVER khud banata hai jab:
1. Naya user signup kare → Free
   subscription automatically ban
   jaaye
2. Payment successful ho (Razorpay
   se) → Payment log automatically
   ban jaaye

# razorpay_sub_id — yeh NULLABLE hai
# database mein (free plan ke liye
# NULL ho sakta hai)

# Toh Pydantic mein bhi Optional
# likhna padega:

razorpay_sub_id: Optional[str] = None

# Warna Pydantic ERROR dega jab
# database se NULL value aayegi!

GOLDEN RULE:

Jab bhi Response schema likho,
HAMESHA model check karo:

Model mein:          Schema mein:
DateTime(...)    →   datetime
Date(...)        →   date
Time(...)        →   time

Aur:
nullable=True    →   Optional[type] = None
nullable=False   →   type (seedha)

Yeh 2 rules follow karo, kabhi
type mismatch nahi hoga!

========================================================

==========================================================

# modules/payments/services.py

* Payment Flow Mein 2 Steps Hote Hain

STEP 1 — "Order Create Karo"
User: "Main Pro plan lena chahta hoon"
        ↓
Hum Razorpay ko bolte hain:
"Ek order banao, ₹499 ka"
        ↓
Razorpay order_id deta hai
        ↓
Hum yeh order_id FRONTEND ko bhejte
hain (Frontend Razorpay payment
popup kholta hai)


STEP 2 — "Webhook Se Confirmation"
User payment kar deta hai
        ↓
Razorpay HUMEIN automatically
batata hai (webhook se):
"Payment successful ho gaya!"
        ↓
Hum database update karte hain:
- User ka plan = "pro"
- PaymentLog banate hain


# razorpay_client.order.create({...})
ye Razorpay ki library ke function hai
hamari taraf se Razorpay ko "order create karo" bolte h

# amount: current_rupee * 100

Razorpay PAISE mein kaam karta hai!

₹499 → 49900 paise

Agar user ne 499 diya, hum khud
*100 karke Razorpay ko bhejte hain!

# "payment_capture": 1
ye batata hai payment turant capture (le lo) - hold mat karo

1 - means turant capture karo 
0 - means manual capture (bad me)


# verify_and_save_payment()
- Ye sabse important function hai
- Jab Razorpay webhook bhehe, ye function:
1. payment details save kare (PaymentLog table me)
2. User ka plan update karo (Subscription table me)

========================================================

==========================================================
# modules/payments/routes.py
# async def razorpay_webhook(request: Request, ...):
normal routes mein hum
Pydantic schema use karte the:

def create_task(task_data: TaskCreate, ...)

Lekin webhooks mein, RAZORPAY jo
data bhejta hai uska EXACT format
hum control nahi karte!

Isliye "Request" object use karte
hain — RAW data directly padhne
ke liye!

await request.json()
= "Jo bhi JSON aaya hai, seedha
   uthao — schema validate mat
   karo abhi!"

# create_order() ko UPDATE karna
# padega — user_id "notes" mein
# bhejna hoga:

def create_order(amount_rupees: int, user_id: str):
    order = razorpay_client.order.create({
        "amount": amount_rupees * 100,
        "currency": "INR",
        "payment_capture": 1,
        "notes": {
            "user_id": user_id  # ← Yeh important hai!
        }
    })
    return order

Kyun zaroori hai?

Jab Razorpay WEBHOOK bhejega,
usse pata NAHI hoga "yeh FlowMate
ka kaunsa user hai"

"notes" field mein hum apna DATA
attach kar sakte hain — Razorpay
yeh SAME data webhook mein WAPAS
bhej deta hai!