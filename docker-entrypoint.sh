#!/bin/bash
set -e

echo "🏰 Fortress AI — Starting backend..."

# Run Prisma migrations (push schema to DB)
echo "📦 Pushing Prisma schema to database..."
prisma db push --skip-generate 2>&1 || echo "⚠️  Prisma push failed (DB might not be ready yet)"

# Start the FastAPI server
if [ "$#" -gt 0 ]; then
    echo "🚀 Executing custom command: $@"
    exec "$@"
else
    echo "🚀 Starting Uvicorn on port 8080..."
    exec uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
fi
