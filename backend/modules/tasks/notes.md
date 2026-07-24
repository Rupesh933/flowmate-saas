# routes.py
- GET /tasks
- POST /tasks
- PUT /tasks/{id}
- DELETE /tasks/{id}

# models.py
- TASKS and TASK_SKIP_LOGS tables

# schemas.py
- TaskCreate, TaskUpdate, TaskResponse - data validation

# services.py
- Task logic + event publish: "task_completed" fire event


==============================================================

uuid.UUID → UUID object banane (parse karne) ke liye class hai.
uuid.uuid4() → Naya random UUID generate karne ke liye function hai.

# modules/tasks/models.py
user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
Forignkey("users.id") --> ye Column User table ke id Column se link hai
means:
- har tasks kisi user ka hoga
- bina userr ke task bn hi nhi skta hai (nullable=False)
- ye multi-tenancy ka base hai

staus = Column(String, default="pending")
- 3 possible values:
1. "pending"  --> abhi karna hai
2. "done" --> complete kar liya
3. "skipped" --> Skip kr diya (AI ye track karega)

priority = Column(Integer, default=3)
1 = Bahut urgent  🔴
2 = Important     🟠
3 = Normal        🟡 (default)
4 = Low           🟢
5 = Very Low      ⚪
=========================================================================

===========================================================================
# modules/tasks/schemas.py
TaskCreate --> sirf jo User bhejega (sirf title required, baki sab optional)
TaskUpdate --> yahan ham sub kuchh optional rakhenge kyuki ho skta hai user sirf status update karna chahta ho ya fir ho skta hai user sifr title update karna chahta ho.
TaskResponse --> DB se jo wapas bhejenge, user_id bhi include (transprency ke liye)
=============================================================================

================================================================================
# models/tasks/services.py
Tasks ka services
GET -- sirf apna task
.filter(Task.user_id == user_id)

UPDATE -- sirf apna task update kar sako!
.filter(Task.id == task_id, Task.user_id == user_id)

DELETE -- sirf apna task delete kar sako
.filter(Task.id == task_id, Task.user_id == user_id)

# update_data = task_data.model_dump(exclude_unset=True)
exclude_unset = True 
means sirft wo field lo jo user ne actually bheja hai, default value ko ignore karo
Example: User ne sirf status bheja:
{"status": "done"}

exclude_unset=True  → {"status": "done"}
exclude_unset=False → {"status": "done", "title": None,
                        "priority": None, ...}

Pehle wala sahi — sirf status update hoga,
baaki fields touch nahi honge!

=============================================================================

====================================================================================
# TaskSkipLogs
man lo priya mostly time 3-5 me distrected hoti hai
tab ai dekhe:
* Priya hamesha physics task skip karti hai or reason hamesha distrected hi hoti hai
* or ye chij mostly 3-5pm ke bich me hoti hai 
* Tab AI physics task ko morning 9am me dr dena ka suggest karega - tab priya free or fresh bhi hoti hai

ham TaskSkipLogs ko alag table me isliye rakhte h kyuki man lo skip_reason = 'distrected' hai or alga skip aaya 'tired' tab ye paihle wale se overwrite ho jayega
* Tab AI ko pattern nhi mil payega - or AI samajh nhi payega

Alag table mein:
Har skip = Naya ROW!

id        | task_id    | user_id    | skip_reason  | skipped_at
----------|------------|------------|--------------|------------
log-001   | task-001   | priya-002  | distracted   | Mon 3:00 PM
log-002   | task-001   | priya-002  | tired        | Tue 3:00 PM
log-003   | task-001   | priya-002  | distracted   | Wed 3:00 PM
log-004   | task-001   | priya-002  | distracted   | Thu 3:00 PM

Koi data loss nahi! 4 skips = 4 rows ✅
AI sab dekh sakta hai! ✅

complete flow
Step 1: Priya "Physics padhna" task banati hai
        → TASKS table mein ek row

Step 2: 3 PM aaya — Priya ne skip kiya
        → POST /tasks/{id}/skip
           {"skip_reason": "distracted"}

Step 3: service.py kya karta hai:
        a) TASKS table mein status = "skipped" karo
        b) TASK_SKIP_LOGS mein naya row daalo:
           {task_id, user_id, "distracted", "3:00 PM"}

Step 4: Yahi kaam baar baar hota rahe →
        Skip logs table bhar jaata hai data se

Step 5: AI /skip-patterns check kare:
        {
          "total_skips": 8,
          "reasons": {
            "distracted": 6,
            "tired": 2
          }
        }

Step 6: AI suggest kare:
        "3-5 PM mein tasks mat rakho — tab tum
         hamesha distracted hoti ho!" 🤖
==========================================================================