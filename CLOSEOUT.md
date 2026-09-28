# aigc-detector · Closeout

- **Control cycle goal:** release-ready (self-host via Compose), not algorithm depth / multi-cloud.
- **Approver (A):** hoyo0210 — accepted with 「可发布」.

## Criteria scorecard

| # | Success criterion | Result |
|---|-------------------|--------|
| 1 | Secrets not in git; prod path uses `.env` / secrets | Pass |
| 2 | `GET /api/health` usable | Pass (`status=ok`, no key leak) |
| 3 | At least one E2E Compose path | Pass (`docker compose`; frontend `:8080`→80, backend `:8000`) |
| 4 | One real `/api/detect` smoke | Pass (direct `:8000` and via Nginx `:8080/api`) |
| 5 | README/DEPLOYMENT consistent; LICENSE present | Pass |

## Acceptance evidence

- Health + security tests: `backend/tests/test_health_security.py` (2 passed)
- Compose: backend healthy; frontend HTTP 200; Nginx `/api/health` OK
- Smoke detect: `label=ai`, `score≈0.98`, `confidence=high` (backend + Nginx)
- A verbal/chat acceptance: 「可发布」

## Leftovers (owned / not this baseline)

- Docker Hub push, multi-cloud recipes, HTTPS/CDN/domain, full observability stack — **Out**; open a new cycle if needed
- Uncommitted local WIP beyond this cycle’s files — owner: A; review before push
- `backend/.env` is local-only — do not commit

## Handoff

- Run: `./deploy.sh` or `docker compose up -d --build` after `backend/.env` with `DASHSCOPE_API_KEY=sk-…`
- Frontend default: `http://localhost:8080` (`FRONTEND_PORT` to override)
- Backend: `http://localhost:8000/api/health`, docs `/docs`
- Stop: `docker compose down`

## Lessons (actionable)

1. **Document the host port that the container actually listens on** (Nginx `:80` ≠ Vite `:5173`); verify Compose mappings on a machine that already has other stacks.
2. **Treat “release-ready” as a thin In/Out baseline** so Out items (Hub, multi-cloud) do not block acceptance.
3. **Same-origin `/api` via Nginx** removes most browser CORS pain for the Compose path; keep `CORS_ORIGINS` for direct API / local Vite.

## This project cycle will not do…

- Detection-model R&D, Zhuque feature parity, forced public domain, or publishing to Docker Hub/PyPI/NPM as part of this closed baseline.

- **Closed by / date:** hoyo0210（A 验收「可发布」）· 2026-09-29 01:41 CST
