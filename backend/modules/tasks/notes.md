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