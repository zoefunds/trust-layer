#!/usr/bin/env bash
set -e

echo "==> Setting up TrustLayer development environment"

# Generate secrets
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
WALLET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Create .env from template
if [ ! -f apps/api/.env ]; then
  cp apps/api/.env.example apps/api/.env
  sed -i '' "s/your-32-char-secret-key-here-change-this/$SECRET_KEY/" apps/api/.env
  sed -i '' "s/your-64-char-hex-key-here/$WALLET_KEY/" apps/api/.env
  echo "✓ Created apps/api/.env"
else
  echo "! apps/api/.env already exists, skipping"
fi

# Start PostgreSQL via Docker
echo "==> Starting PostgreSQL..."
docker compose -f infrastructure/docker/docker-compose.yml up -d postgres

echo "==> Waiting for PostgreSQL..."
sleep 5

echo ""
echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. cd apps/api && pip install -r requirements.txt"
echo "  2. uvicorn app.main:app --reload --port 8000"
echo "  3. cd apps/web && npm run dev"
echo ""
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API docs: http://localhost:8000/docs"
