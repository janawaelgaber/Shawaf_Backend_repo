# Local backend deployment

## Omar's changes

| Ticket | What this branch adds |
| --- | --- |
| [SCRUM-16](https://shawaf.atlassian.net/browse/SCRUM-16) | Local Compose stack for PostgreSQL, Redis, MinIO, Nginx, and FastAPI. Adds FastAPI liveness and readiness endpoints, private media bucket setup, and automatic CORS configuration when an origin is set. |
| [SCRUM-45](https://shawaf.atlassian.net/browse/SCRUM-45) | CPU and optional GPU Celery workers, Celery Beat, Redis heartbeats, late acknowledgments, and redelivery on worker loss. |
| [SCRUM-46](https://shawaf.atlassian.net/browse/SCRUM-46) | Four Redis-backed Celery queues. Video processing selects the CPU or GPU queue. Clip and callback tasks have explicit routes. |
| [SCRUM-93](https://shawaf.atlassian.net/browse/SCRUM-93) | Helpers to add a pending callback in the caller's database transaction, plus a registered Celery task that reads the outbox row, signs and sends the HTTP request, and records an accepted receipt. An HTTP 500 leaves the row pending. |

## Start the stack

From the repository root, with Docker running:

```powershell
cd deployment
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
docker compose up -d
docker compose ps -a
```

After changing the Python code or dependencies, rebuild the services that use the Python image:

```powershell
docker compose up -d --build inference-api inference-worker-cpu inference-beat
```

| Service | Role |
| --- | --- |
| `postgres` | Database `shawaf`. NestJS uses schema `app` with `shawaf_app`. FastAPI uses schema `analytics` with `shawaf_ai`. The local bootstrap account is `shawaf_local`. |
| `redis` | Celery broker on the Compose network at `redis://redis:6379/0`. |
| `minio`, `minio-init`, `minio-cors` | Object storage on port 9000 and setup for the private `shawaf-media` bucket. The two setup containers exit when their work finishes. |
| `inference-api` | FastAPI on host port 8000 for direct local testing. |
| `inference-worker-cpu` | Celery worker for `pipeline.cpu`, `media.clips`, and `callbacks`. |
| `inference-beat` | Celery scheduler. |
| `proxy` | Nginx on host port 80. Requests under `/internal/` return HTTP 403 through the proxy. |

PostgreSQL and MinIO use named volumes to preserve local data across container restarts. The current proxy configuration covers the internal-route guard. Public NestJS forwarding is pending integration.

## Verify the stack

Run these commands from `deployment`:

```powershell
(Invoke-RestMethod "http://localhost:8000/internal/v1/health/ready").data
curl.exe -i http://localhost/internal/v1/health/live
docker compose logs --tail=50 inference-worker-cpu inference-beat
docker compose exec inference-worker-cpu celery -A ai.workers.celery_app:celery_app inspect ping
```

With the dependencies ready, the first command reports `postgres`, `redis`, and `bucket` as `up`. The proxy request returns `403 Forbidden`. The CPU worker logs show `ready` after connecting to Redis, and `inspect ping` returns `pong`.

## Optional GPU worker

```powershell
docker compose --profile gpu up -d --build inference-worker-gpu
docker compose logs --tail=35 inference-worker-gpu
docker compose --profile gpu stop inference-worker-gpu
```

The GPU worker listens on `pipeline.gpu` with concurrency set to 1. This startup check verifies the worker's Redis connection and queue subscription. Running GPU workloads also requires GPU access inside the container and task code that uses it.

## Browser upload CORS

Set `FRONTEND_ORIGIN` in `deployment/.env` to the approved frontend origin (scheme, host, and port if applicable). Leave it empty until an origin is assigned. An empty value makes the setup script skip changes to the bucket, including any rule already stored there.

On startup, Compose runs `minio-cors` after bucket creation succeeds. Check the result with `docker compose logs minio-cors`. A configured origin enables the browser upload rule. An empty origin skips configuration.

## Callback delivery

The CPU worker consumes `callbacks.deliver` with an outbox UUID and posts the stored body to `backend:4000`. Its local defaults use the analytics database role and the example signing secret. Set `AI_TO_NEST_HMAC_SECRET` to the same value as the NestJS verifier for integration. The Compose database hostname is `postgres`.

## Verification and integration

- Verified locally that FastAPI reports its dependencies up, the proxy returns HTTP 403 on internal routes, and PostgreSQL roles can access their assigned schemas. Checked volume persistence and anonymous MinIO access.
- Verified Celery queue assignments, heartbeat updates, and redelivery after worker loss. The in-flight shutdown test used a 45-second grace period.
- Verified callback insert commit and rollback against a disposable PostgreSQL database. Tested signed delivery through Redis and Celery to an HTTP stub. An accepted receipt saved `delivered`, and an HTTP 500 preserved `pending`.
- Tested automatic CORS setup against a fresh bucket. The configured origin's preflight succeeded and an unrelated origin received HTTP 403.
- Run the end-to-end callback and public proxy checks with NestJS once the service is available as `backend:4000` on the Compose network. Apply Ola's [SCRUM-138](https://shawaf.atlassian.net/browse/SCRUM-138) analytics migration for shared integration. Callback retry policy is tracked in [SCRUM-92](https://shawaf.atlassian.net/browse/SCRUM-92).
- Verify the one-second readiness budget under slow dependencies and the default Compose shutdown grace period with an in-flight task.
