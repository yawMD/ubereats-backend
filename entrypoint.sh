#!/bin/sh

# Wait for the database to be ready
echo "Waiting for PostgreSQL to become available..."
while ! nc -z $DB_SERVICE $DB_PORT; do
  sleep 0.1
done
echo "PostgreSQL is available now."

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Start the application
echo "Starting the server..."
exec "$@"
