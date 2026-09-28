#!/usr/bin/env bash
# One-path Compose deploy for aigc-detector (release-ready minimum).
set -euo pipefail

COMPOSE=(docker compose)
if ! docker compose version &>/dev/null; then
  if command -v docker-compose &>/dev/null; then
    COMPOSE=(docker-compose)
  else
    echo "Docker Compose not found. Install Docker Desktop or the compose plugin."
    exit 1
  fi
fi

echo "AI Detector — Compose deploy"
echo "============================"

if ! command -v docker &>/dev/null; then
  echo "Docker is not installed."
  exit 1
fi

if [[ ! -f backend/.env ]]; then
  if [[ -f backend/.env.example ]]; then
    cp backend/.env.example backend/.env
    echo "Created backend/.env from .env.example"
    echo "Edit backend/.env and set DASHSCOPE_API_KEY=sk-..., then re-run."
    exit 1
  fi
  echo "Missing backend/.env and backend/.env.example"
  exit 1
fi

if ! grep -qE '^DASHSCOPE_API_KEY=sk-' backend/.env; then
  echo "DASHSCOPE_API_KEY looks unset in backend/.env (expected value starting with sk-)."
  exit 1
fi

# Export key vars so ${VAR} interpolation in compose also works.
set -a
# shellcheck disable=SC1091
source backend/.env
set +a

echo "Building and starting..."
"${COMPOSE[@]}" up -d --build

echo "Waiting for backend health..."
for i in {1..30}; do
  if curl -fsS http://127.0.0.1:8000/api/health >/dev/null; then
    echo "Backend healthy."
    break
  fi
  if [[ $i -eq 30 ]]; then
    echo "Backend health check failed. Logs:"
    "${COMPOSE[@]}" logs --tail=80 backend
    exit 1
  fi
  sleep 2
done

FRONTEND_URL="http://127.0.0.1:${FRONTEND_PORT:-8080}"

if curl -fsS -o /dev/null "$FRONTEND_URL/"; then
  echo "Frontend reachable on $FRONTEND_URL/"
else
  echo "Frontend not reachable on $FRONTEND_URL"
  "${COMPOSE[@]}" logs --tail=80 frontend
  exit 1
fi

echo
echo "Deploy OK"
echo "  Frontend: http://localhost:${FRONTEND_PORT:-8080}"
echo "  Backend:  http://localhost:8000/api/health"
echo "  API docs: http://localhost:8000/docs"
echo
echo "Stop with: ${COMPOSE[*]} down"
