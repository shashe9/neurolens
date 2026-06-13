#!/usr/bin/env bash
set -e

echo "Starting Neurolens Backend Entrypoint..."

# Wait for DB to be ready
echo "Waiting for database to start up..."
python -c "
import sys, time
from sqlalchemy import create_engine
from app.core.config import settings
for i in range(30):
    try:
        engine = create_engine(settings.sqlalchemy_database_url)
        with engine.connect() as conn:
            print('Database is ready!')
            sys.exit(0)
    except Exception as e:
        print('Database not ready yet, sleeping 1s...')
        time.sleep(1)
sys.exit(1)
"

# Run migrations
echo "Running migrations..."
alembic upgrade head

# Seed database
echo "Seeding database..."
python -m app.database.seed

# Exec CMD
echo "Starting application..."
exec "$@"
