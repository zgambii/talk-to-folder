# Development: tests & quality

[← README](../README.md)

## Backend

From `backend/` with the virtualenv active and `pip install ".[dev]"` (see [Local setup](setup.md)):

```bash
pytest
ruff check .
black --check .
```

## Frontend

From `frontend/`:

```bash
npm run lint
npm run build
npm run format:check    # Prettier check
npm run format          # Prettier write
```
