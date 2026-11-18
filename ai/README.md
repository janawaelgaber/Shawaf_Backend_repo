# ai

FastAPI on port 8000, prefix `/internal/v1`.

| Path | Owner |
|---|---|
| `api/`, `workers/`, `pipeline/runner.py`, `media/`, `live/` | Omar |
| `contracts/`, `registry/`, `packages/`, `persistence/`, `pipeline/validation.py`, `api/routes/search.py` | Ola |

`persistence/models.py` is schema `analytics`. SCRUM-138 is the only revision. Create it with:

```bash
alembic -c ai/persistence/alembic.ini revision --autogenerate -m "SCRUM-138 analytics schema"
```

Omar does not add a revision. `workers/celery_app.py` declares `pipeline.gpu`, `pipeline.cpu`, `media.clips`, and `callbacks`. The live worker is not one of those queues.

```bash
pip install -e ".[dev]"
uvicorn ai.api.main:app --port 8000
pytest
```
