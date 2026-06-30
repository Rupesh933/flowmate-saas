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
