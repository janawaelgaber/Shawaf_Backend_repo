# deployment

Omar, SCRUM-16, owns this stack.

```bash
docker compose -f deployment/docker-compose.yml up -d
```

| Service | What the tickets name |
|---|---|
| PostgreSQL `shawaf` | Schema `app` for `shawaf_app`. Schema `analytics` for `shawaf_ai`. |
| Redis | Queues `pipeline.gpu`, `pipeline.cpu`, `media.clips`, `callbacks`. |
| MinIO | Bucket `shawaf-media` on port 9000. |

`shawaf_local` is only the local superuser that creates the two application users. Application code does not use it. RabbitMQ is not part of this stack. NestJS and FastAPI run on the host, not in this file.
