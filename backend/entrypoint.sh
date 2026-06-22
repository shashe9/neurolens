#!/usr/bin/env bash
set -e

echo "Starting Neurolens Backend Entrypoint..."

# Wait for DB to be ready
echo "Waiting for database to start up..."
python -m app.database.wait_for_db

# Run migrations
echo "Running migrations..."
alembic upgrade head

# Seed database conditionally
SEED_VAL=$(echo "${SEED_ON_STARTUP:-false}" | tr '[:upper:]' '[:lower:]')
if [ "$SEED_VAL" = "true" ]; then
    echo "Seeding database..."
    python -m app.database.seed
else
    echo "SEED_ON_STARTUP is false, skipping database seed."
fi

# Exec CMD
echo "Starting application..."
exec "$@"
