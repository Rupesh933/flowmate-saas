# Flowmate Backend Folder Structure

This document outlines the file and folder layout for the `backend` service.

```text
backend/
├── .env                  # Secret keys & environment variables (DATABASE_URL, JWT_SECRET, etc.)
├── alembic.ini           # Configuration for Alembic database migrations
├── main.py               # Application entry point (initializes FastAPI, registers modules & routers)
├── requirements.txt      # Python dependencies list
├── core/                 # Shared core utilities and configuration
│   ├── config.py         # Application configuration (loads .env)
│   ├── database.py       # SQLAlchemy database engine and session setup
│   ├── dependencies.py   # Shared FastAPI dependencies (e.g., get_db)
│   ├── events.py         # App lifecycle event handlers (startup, shutdown)
│   └── redis_client.py   # Redis client connection and helpers
└── modules/              # Feature modules (Domain Driven Design)
    ├── auth/             # Authentication & User Management
    │   ├── models.py     # SQLAlchemy models for Auth (User table)
    │   ├── routes.py     # Auth endpoints (Login, Signup, Logout)
    │   └── schemas.py    # Pydantic schemas for Auth validation
    ├── tasks/            # Task CRUD Operations
    │   ├── models.py     # SQLAlchemy models for Tasks
    │   ├── routes.py     # Task API endpoints
    │   ├── schemas.py    # Pydantic schemas for Tasks
    │   └── services.py   # Business logic for Task management
    ├── ai/               # AI Suggestions & Analysis
    │   ├── routes.py     # AI endpoints
    │   └── services.py   # Core logic for AI calls, suggestions, and analysis
    ├── reminders/        # Automatic Reminders
    │   ├── routes.py     # Reminder endpoints
    │   └── scheduler.py  # APScheduler integration logic
    ├── gamification/     # Fun Layer (Points, badges, streaks)
    │   └── services.py   # Streak and point calculation logic
    └── payments/         # Payment Integrations
        └── routes.py     # Razorpay webhook and checkout endpoints
```

## Detailed Explanations

### Root Files
- **`main.py`**: The main entry point where the FastAPI app is initialized. All CORS settings, middlewares, and routers from various modules are imported and registered here.
- **`requirements.txt`**: Contains all external Python packages required for the project. Run `pip install -r requirements.txt` to install.
- **`alembic.ini`**: Config file for Alembic, used for managing database migrations (schema updates, new tables/columns).
- **`.env`**: Local environment variables configuration (never commit this to GitHub).

### Directories

#### `core/`
Contains common code, utilities, database connections, and configurations shared across multiple modules.
- **`config.py`**: Global application configurations loaded from `.env`.
- **`database.py`**: Sets up SQLAlchemy database engine and `SessionLocal`.
- **`dependencies.py`**: Common dependencies (like database sessions, current user dependencies, etc.).
- **`redis_client.py`**: Establishes connection and manages cache operations via Redis.
- **`events.py`**: Actions to run when the application starts or stops.

#### `modules/`
Self-contained packages representing distinct functional modules of the application:
- **`auth/`**: Standard authentication flows (signup, login, logout) and JWT validation.
- **`tasks/`**: CRUD operations and core task scheduling business logic.
- **`ai/`**: Calls external LLM/AI APIs to provide suggestions and analyze productivity patterns.
- **`reminders/`**: Automatic email/push notification reminders utilizing APScheduler.
- **`gamification/`**: Core engine for user engagement, computing streaks, assigning badges, and tracking points.
- **`payments/`**: Integrates Razorpay payment processing and handles checkout events/webhooks.
