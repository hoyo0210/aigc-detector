# aigc-detector · Cycle 2 Charter (PMP)

- Problem / opportunity: v1.1.0 is Compose-ready, but path-to-runtime lacks automated verify; existing `docker-deploy.yml` pushes images on PRs (wide blast radius).
- Goals: **CI verifies on PR/push**; **GHCR publish only on default-branch push** after checks; health exposes build identity.
- Non-goals: Docker Hub; multi-cloud; mobile; algorithm changes; multi-arch matrix (amd64 only this cycle).
- Success criteria (evidence):
  1. PR/push runs backend pytest (and fails the check on failure)
  2. Image push to GHCR happens on `master` only, after tests
  3. `GET /api/health` includes non-secret `version` (git sha or env)
  4. A accepts with 「可发布」or equivalent
- Approver A: hoyo0210
- Constraints: no secrets in git; public repo; GITHUB_TOKEN for GHCR
- Key assumptions: GitHub Actions enabled; packages:write via GITHUB_TOKEN sufficient
- Stop-loss: GHCR permission failures → keep CI tests, disable push job until fixed
