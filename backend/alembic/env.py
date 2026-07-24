import os
import sys
import socket
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, '.env'))

config = context.config
config.set_main_option(
    "sqlalchemy.url",
    os.getenv("DATABASE_URL")
)

raw_url = os.getenv('DATABASE_URL', '')

# Smart host resolution:
# If 'db' hostname cannot be resolved (running outside Docker),
# fall back to 'localhost' automatically.
def resolve_db_url(url):
    if '@db:' in url:
        try:
            socket.getaddrinfo('db', 5432)
            return url  # inside Docker, 'db' resolves fine
        except socket.gaierror:
            return url.replace('@db:', '@localhost:')  # outside Docker, use localhost
    return url

db_url = resolve_db_url(raw_url)
config.set_main_option('sqlalchemy.url', db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from core.database import Base
from modules.auth.models import User
from modules.tasks.models import Task, TaskSkipLogs
from modules.habits.models import Habit, HabitLog

from modules.reminders.models import Reminder
from modules.ai.models import AiInsights
from modules.gamification.models import Badge, UserBadges, PointsLog
from modules.payments.models import PaymentLog, Subscription

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option('sqlalchemy.url')
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
