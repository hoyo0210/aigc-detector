# aigc-detector · Cycle 2 Closeout

- **Control cycle goal:** CI verify on PR/push; GHCR publish only after tests on default branch/tags; health exposes non-secret `version`.
- **Approver (A):** hoyo0210 — accepted with 「可发布」.
- **Skills used:** `pmp-ai-native` (project control) + `devops-ai-native` (Build/Release path).

## Criteria scorecard

| # | Success criterion | Result |
|---|-------------------|--------|
| 1 | Backend pytest on PR/push | Pass — [CI 36463004478](https://github.com/hoyo0210/aigc-detector/actions/runs/36463004478) |
| 2 | GHCR push on `master` only, after tests | Pass — [Publish 36463004662](https://github.com/hoyo0210/aigc-detector/actions/runs/36463004662) |
| 3 | `/api/health` includes `version` | Pass — code + tests |
| 4 | A acceptance | Pass — 「可发布」 |

## Acceptance evidence

- Commits: `7a5a627`, `23ba403`
- Workflows: `.github/workflows/ci.yml`, tightened `docker-deploy.yml`
- Local: `PYTHONPATH=. pytest` 2 passed; frontend `npm run build` OK before push

## Leftovers

- `mobile/` still untracked — Out
- Multi-arch / Docker Hub / public URL — Out
- Node 20 deprecation annotations on Actions — follow-up later

## Handoff

- PRs: watch **CI** (pytest + frontend build)
- `master` / `v*` tags: **CI** + **Build and publish image** → `ghcr.io/hoyo0210/aigc-detector`
- Compose self-host unchanged (`./deploy.sh`, frontend `:8080`)

## Lessons

1. **Fix push-on-PR image workflows early** — wide blast radius and wasted registry noise.
2. **PAT without `workflow` scope blocks workflow file pushes** — use `gh auth` token with `workflow`.
3. **PMP charter + DevOps Build stage pair cleanly**: scope/In-Out first, then pipeline as the deliverable.

## This cycle will not do…

- Mobile packaging, Hub mirroring, arm64 matrix, algorithm work.

- **Closed by / date:** hoyo0210 · 2026-09-29 02:10 CST
