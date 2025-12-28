# Repository Guidelines

## Project Structure & Module Organization
- `tex_tailor/` holds the Python CLI core (extract, propose, apply, diff, render) plus shared utilities.
- `tex_tailor/tests/` contains Python unit tests (unittest).
- `frontend/` is the Vue 3 app; the Express API lives in `frontend/server/` and UI components in `frontend/src/`.
- `templates/` stores baseline LaTeX resume/cover-letter templates used by the CLI.
- `scripts/` includes workflow helpers (batch runs, LaTeX checks).
- `docs/` contains architecture, API, and deployment references.

## Build, Test, and Development Commands
- `./run_local_dev.sh`: boots the local dev environment (Python venv checks + `npm run dev`).
- `cd frontend && npm install`: install frontend dependencies.
- `cd frontend && npm run dev`: start Vite dev server + API (`http://localhost:3000`).
- `cd frontend && npm run build`: production build of the UI.
- `./test_docker_build.sh`: build and run the production Docker image locally.
- `./scripts/run_workflow.sh path/to/jd.txt`: end-to-end CLI workflow against a job description.
- `python -m unittest discover -s tex_tailor/tests`: run Python unit tests.

## Coding Style & Naming Conventions
- Python: 4-space indentation, `snake_case` for modules/functions, keep CLI-friendly output messages.
- Vue/JS: 2-space indentation, PascalCase for components (e.g., `ProviderSelector.vue`).
- Follow existing formatting; no repo-wide formatter/linter is enforced.

## Testing Guidelines
- Framework: Python `unittest` in `tex_tailor/tests/` with `test_*.py` names.
- Prefer small, deterministic tests for parsing/patching logic; avoid real API calls.

## Commit & Pull Request Guidelines
- Commit messages in history are short, lowercase phrases (e.g., “fixed refresh”).
- PRs should describe the change, link relevant issues if available, and include UI screenshots for frontend-facing work.

## Configuration & Secrets
- Environment variables and provider configuration live in `docs/CONFIG.md`.
- Do not commit API keys; use local environment variables or the Settings UI.
