# AGENT.md (Codex Rules)

## Mission
Build a web app that:
- Searches professors by topic + university (OpenAlex)
- Shows ranked professors + top relevant papers
- Takes pasted resume text
- Generates a personalized cold email template (no hallucinated claims)

## Hard rules (must always follow)
1) Run tests before finishing any task:
   - Backend: `cd backend && python -m pytest -q`
2) Never log or store resume_text.
3) Never commit secrets (.env, API keys).
4) Do not make network calls in tests; mock OpenAlex responses.
5) Keep changes small and incremental. If a change is risky, add tests first.

## Definition of done for any change
- Code compiles
- Tests pass
- No secrets added
- CI should pass

## Current MVP endpoints
- GET /api/health
- GET /api/universities?q=
- POST /api/search
- POST /api/email/generate

## Current stack
- Backend: FastAPI, httpx, pytest
- Frontend: React + Vite (later)
- OpenAlex API only