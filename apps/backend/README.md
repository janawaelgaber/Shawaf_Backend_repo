# apps/backend

NestJS on port 4000. Public prefix `/api/v1`. Callbacks stay on `/internal/v1`.

| Path | Owner |
|---|---|
| `src/auth`, `src/users`, `src/organizations`, `src/health`, `src/common/auth`, `src/config` | Jana |
| `prisma/`, `src/storage`, `src/cameras`, `src/videos`, `src/clips` | Rokayya |
| `src/common/hmac`, `src/inference-client`, `src/internal-callbacks`, `src/search`, `src/alerts` | Labib |
| `src/cases`, `src/notifications` | Phase 2. Not imported. |

`prisma/schema.prisma` lists the columns the tickets already name. Rokayya runs the migration for the ticket that writes the table. Session, invitation, and seal-idempotency tables are not in this schema. She and Jana choose those layouts on their tickets.

```bash
npm install
npx prisma generate
npm run start:dev
```
