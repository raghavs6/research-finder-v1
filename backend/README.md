# Backend

## Run API locally

From repository root:

```bash
./backend/.venv/bin/python -m uvicorn app.main:app --reload --app-dir backend
```

From backend directory:

```bash
cd backend
.venv/bin/python -m uvicorn app.main:app --reload
```

If port `8000` is already in use:

```bash
cd backend
.venv/bin/python -m uvicorn app.main:app --reload --port 8001
```

## Verify API is up

Default port (`8000`):

```bash
curl http://127.0.0.1:8000/api/v1/health
```

If you used `--port 8001`, replace `8000` with `8001`.

## Common startup errors

- `zsh: command not found: uvicorn`
  - Use the virtualenv executable path: `.venv/bin/python -m uvicorn ...`
- `Error loading ASGI app. Could not import module "main"`
  - The app module is `app.main:app`, not `main:app`.
- `Address already in use`
  - Another process is using the selected port. Use `--port 8001` (or free the port).

## Run tests

From repository root:

```bash
./backend/.venv/bin/python -m pytest -q backend/tests
```

From backend directory:

```bash
cd backend
.venv/bin/python -m pytest -q tests
```
