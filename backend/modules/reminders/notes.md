# routes.py
- POST /reminders  - set the reminder

# scheduler.py
- Background jobs - check every minutes, time come? send!


=========================================
# modules/reminders/scheduler.py

# from apscheduler.schedulers.asyncio import AsyncIOScheduler
This imports AsyncIOScheduler from APScheduler.
APScheduler = Advanced Python Scheduler
It allows you to run functions automatically at specific times.

# scheduler.add_job(my_function, "interval", minutes=5)
- Every 5 minutes → execute my_function()
- Here you are using the asyncio version because FastAPI is async-friendly.

# scheduler = AsyncIOScheduler()
- Creates scheduler object.

# SessionLocal()
- SessionLocal ek session factory hai
- sessionlocal() karne par ek new DataBase session milega
- Usually core/database.py 

# get_db()
- FASTAPI me normally
- ye ek dependency function hai
iska kam:
- session banana
- Endpoint ko dena
- Request complete hone ke bad close karna

# schedular me db: Session = SessionLocal()
- yahan direct SessionLocal() ka use huva hai kyuki ye FASTAPI request nhi hai 
- ek new database session banao aur use db variable me store karo
- get_db kyu nhi - iska reason hai ki schedular ke pass fastapi request nhi hoti.
APSedular bol raha hai - Har ek minute ke bad check_reminders() function chalao
    Yahan koi:

    - browser nahi hai
    - API request nahi hai
    - route nahi hai
    - FastAPI dependency system nahi chal raha

    Bas ek normal Python function run ho raha hai.