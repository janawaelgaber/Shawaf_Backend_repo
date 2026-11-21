# SHAWAF backend

This is the backend code repository. NestJS, FastAPI, workers, and the local stack are committed here. Reading material stays in the private tasks repository: [shawaf](https://github.com/Nabillco/shawaf).

`main` is the shared line. A member commits on their own branch and opens a pull request into `main`. Omar Mahmoud reviews that pull request and merges it. Nobody else merges into `main`.

## Branches

| Member | Branch | Code in this repository |
|---|---|---|
| Jana Wael | `jana` | `apps/backend` shell, login, scope, invitations, health |
| Rokayya Aly Hosny | `rokayya` | `apps/backend` Prisma schema `app`, storage, cameras, videos, clips |
| Ahmed Mahmoud Labib | `labib` | `apps/backend` HMAC client, callbacks, search, alerts |
| Omar Mahmoud | `omar` | `ai` API and workers, `deployment` |
| Ola Omara | `ola` | `ai` packages, checks, and the `analytics` migration |

Clone the repository and switch to your own branch from the table. Jana uses `jana`. Rokayya uses `rokayya`. Labib uses `labib`. Omar uses `omar`. Ola uses `ola`.

```bash
git clone https://github.com/Nabillco/shawaf-backend.git
cd shawaf-backend
git checkout <your-branch>
```

Update your branch from `main`, commit, and push that same branch:

```bash
git pull origin main
git merge main
git push -u origin <your-branch>
```

Open a pull request into `main`. This example is Jana's branch. Each person uses their own branch name.

```bash
gh pr create --base main --head jana --title "SCRUM-24 login" --body "Implements the login ticket."
```

The member opens that pull request. Omar reviews it on GitHub and presses merge. A member does not merge their own pull request, except Omar when the branch is `omar`. Do not push directly to `main`, and do not force-push `main`.

The owner invites each person from **Settings → Collaborators**. Use that person's GitHub username.

## What you need while coding

The browser calls NestJS on port `4000` at `/api/v1`. NestJS calls FastAPI on port `8000` at `/internal/v1`. Python calls NestJS back at `/internal/v1`.

PostgreSQL database `shawaf` has two schemas. `shawaf_app` writes `app`. `shawaf_ai` writes `analytics`. There is no foreign key between them. Rokayya adds Prisma migrations for `app`. Ola's SCRUM-138 is the only Alembic migration for `analytics`.

Redis queues are `pipeline.gpu`, `pipeline.cpu`, `media.clips`, and `callbacks`. A processing message is `job_id` only. Object storage is the bucket `shawaf-media`.

HMAC uses `NEST_TO_AI_HMAC_SECRET` from NestJS to FastAPI and `AI_TO_NEST_HMAC_SECRET` from Python to NestJS.

Phase 1 does not wait for Phase 2. Do not add a field, table, or error code that the ticket does not name. Unspecified behavior is listed in the tasks repository at `02-Backend-Implementation-Guides/07-Open-Decisions.md`.

## Where the contracts are

| Question | Read this in `shawaf` |
|---|---|
| Your tickets | `02-Backend-Implementation-Guides/` |
| Columns | `01-API-Contract/10-database-erd.md` |
| Public JSON | `01-API-Contract/openapi/public-api.v1.yaml` |
| Internal JSON | `01-API-Contract/openapi/internal-inference-api.v1.yaml` and `internal-callbacks.v1.yaml` |
| Folders | `01-API-Contract/07-repository-layout.md` |

## Layout

```text
apps/web/         Frontend placeholder. Empty until the frontend ticket.
apps/backend/     NestJS on port 4000. Jana, Rokayya, and Labib.
ai/               FastAPI on port 8000, workers, and analytics models. Omar and Ola.
deployment/       PostgreSQL, Redis, and MinIO. Omar, SCRUM-16.
contracts/        Shared contract files. Empty placeholder for now.
scripts/          repo_tree.py checks this layout (SCRUM-120).
```

`apps/api`, `apps/ml-api`, and `apps/worker` must not exist. Check the layout with `python scripts/repo_tree.py`.

The processes start. The ticket handlers are still empty. Each member fills the module named on their ticket. Do not add a column, route, or error code the ticket does not name.

## Run it locally

```bash
docker compose -f deployment/docker-compose.yml up -d
```

Copy `deployment/.env.example` to `deployment/.env` before using Prisma. NestJS does not need the database just to boot.

```bash
cd apps/backend
npm install
npx prisma generate
npm run start:dev
```

From the repository root, in another terminal:

```bash
pip install -e ".[dev]"
uvicorn ai.api.main:app --port 8000
```

Rokayya adds each Prisma migration with the ticket that writes that table. Ola's SCRUM-138 is the only Alembic revision, from `ai/persistence`:

```bash
alembic -c ai/persistence/alembic.ini revision -m "SCRUM-138 analytics schema"
```

Omar does not add an Alembic revision. Phase 2 modules `src/cases` and `src/notifications` exist and are not imported.
