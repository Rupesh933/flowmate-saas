# services.py
- add Points
- check badge
-- listen event

===============================
# modules/gamification/services.py
def add_points(
    db: Session,
    user_id: uuid.UUID,
    point: int,
    reason: str,
    source_type: str
) -> PointsLog:
Tum pooch rahe ho: "add_points mein
PointsLog kyun bana rahe hain?"

Chalo REAL LIFE se samjhte hain:

Socho tumhara BANK ACCOUNT hai:

Jab bhi paisa aata hai (salary, gift, etc.)
Bank EK NAYI ENTRY banata hai passbook mein:

Date       | Description      | Amount
-----------|-------------------|--------
Jan 1      | Salary            | +50000
Jan 15     | Gift from mummy   | +5000
Jan 20     | Freelance         | +10000

Total Balance = 50000+5000+10000 = 65000

BILKUL WAHI concept hai yahan:

PointsLog = Tumhari "Points Passbook"

Har baar jab user koi kaam kare:
  Task complete    → +10 points → NAYI ROW
  Habit log        → +10 points → NAYI ROW
  7-day streak     → +50 points → NAYI ROW

PointsLog Table:
user_id | points | reason           | source_type
--------|--------|------------------|------------
rahul   | +10    | Task done        | task
rahul   | +10    | Habit logged     | habit
rahul   | +50    | 7-day streak     | streak

Total Points = 10+10+50 = 70
==========================================

===============================================
# modules/gamification/routes.py
Dusre modules mein:
User khud request bhejta hai
POST /tasks → User task banata hai
POST /habits → User habit banata hai

Gamification mein:
add_points() USER KHUD call NAHI karta!

Yeh hota hai jab:
- Task complete ho (Tasks module se call hoga)
- Habit log ho (Habits module se call hoga)

User sirf DEKHEGA:
- Apne badges (GET request)
- Apni points history (GET request)

Sirf 2 GET Routes:

GET /gamification/badges   → Apne badges dekho
GET /gamification/points   → Apni points history dekho

add_points() ka KOI ROUTE NAHI!
(Yeh andar se call hoga, baad mein
 jab hum Tasks/Habits module update
 karenge to add_points() call karenge)

 BADGES table mein 3 badges hain (Master List)
  → "7-Day Warrior", "Early Bird", "Task Master"

Lekin GET /gamification/badges kya return karta hai?
  → services.get_user_badges() call hota hai
  → Yeh UserBadges table dekhta hai
     (NOT Badges table!)

UserBadges table = "KISNE KAUNSA badge EARN kiya"

2 Alag Table
BADGES table (Master List):
┌─────────────────┬──────────────────┐
│ name             │ required_points  │
├─────────────────┼──────────────────┤
│ 7-Day Warrior    │ 70               │
│ Early Bird       │ 100              │
│ Task Master      │ 500              │
└─────────────────┴──────────────────┘
        ↑
   Yeh tumne INSERT kiya — sahi!


USER_BADGES table (Kisne Kya Earn Kiya):
┌─────────┬───────────┬────────────┐
│ user_id │ badge_id  │ earned_at  │
├─────────┼───────────┼────────────┤
│ (khaali abhi tak!)              │
└─────────┴───────────┴────────────┘
        ↑
   Yeh KHAALI hai kyunki
   abhi tak KISI NE koi
   points hi nahi kamaye!

GET /gamification/points Bhi Khaali Kyun Hai?
Yeh POINTS_LOG table check karta hai

PointsLog = "Kab kab points mile"

Abhi tak add_points() function
KABHI CALL nahi hua!

Kyun?
Kyunki humne abhi Tasks/Habits module
mein add_points() ko CALL nahi kiya!

Task complete karo → add_points() call hona chahiye
                      → Lekin abhi wahan yeh
                        line nahi hai!

<Yeh Bilkul Normal Hai — Real Life Se Samjho>
Socho tumne ek NAYA bank account khola

Bank ki "Fixed Deposit Schemes" list:
  → 5% interest, 6% interest, 7% interest
  (Yeh BADGES table jaisa hai — options hain)

Tumhara "Transaction History":
  → KHAALI! (Kyunki tumne abhi
    koi paisa deposit nahi kiya)

Jaise hi paisa deposit karoge:
  → Transaction history mein entry aayegi!
  → Agar enough balance ho gaya,
    FD scheme "unlock" ho jaayegi!