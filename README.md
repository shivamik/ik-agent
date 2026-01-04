# ik-agent

Python tool wrappers around the ImageKit SDK, plus helper utilities and tests.

## Setup
- Python 3.12 recommended.
- Create a venv and install dependencies (use your preferred workflow).
- Set required environment variables:
  - `IMAGEKIT_PRIVATE_KEY`

## Project Layout
- `src/` — tool implementations and shared utilities.
- `tests/` — pytest suite.
- `notebooks/` — ad-hoc notebooks (e.g., smoke calls).
- `mcp-server/` — upstream TS tool definitions.

## Run Tests
```bash
make local-tests
```

## Tools Status
See `TOOLS_STATUS.md` for the implementation tracker.

## Smoke Calls Notebook
Use `notebooks/tools_smoke_calls.ipynb` for quick, manual tool checks.
It contains safe calls by default and leaves destructive or ID-dependent calls commented.
