FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (libatomic1 needed by Prisma CLI's bundled Node.js)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libatomic1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure entrypoint is executable
RUN chmod +x docker-entrypoint.sh

# Prisma generate during build (to have types ready)
RUN prisma generate

ENTRYPOINT ["./docker-entrypoint.sh"]

