import boto3
from botocore.config import Config
import psycopg
import redis

from fastapi import APIRouter
router=APIRouter()

# SCRUM-16 allows one second per readiness check. Client timeouts cover individual
# operations, so the full Postgres, Redis, or MinIO probe can take longer.
# Measure each probe end to end under slow responses before tuning its timeouts.
#if it work correctly it will send up if not it will send down
def _up(check)->str:
    try:
        check()
        return "up"
    except Exception:
        return "down"

    
def _check_postgres() -> None:
    with psycopg.connect(
        host="postgres",
        port=5432,
        dbname="shawaf",
        user="shawaf_ai",
        password="shawaf_ai",
        connect_timeout=1,
    ) as connection:
        connection.execute("SELECT 1")

def _check_redis()->None:
    client = redis.Redis(host="redis", port=6379, socket_connect_timeout=1, socket_timeout=1)
    client.ping()

def _check_bucket() -> None:
    client = boto3.client(
        "s3",
        endpoint_url="http://minio:9000",
        aws_access_key_id="shawaf_local",
        aws_secret_access_key="shawaf_local",
        region_name="us-east-1",
        config=Config(
            connect_timeout=1,
            read_timeout=1,
            retries={"total_max_attempts": 1},
            s3={"addressing_style": "path"},
        ),
    )
    client.head_bucket(Bucket="shawaf-media")

@router.get("/internal/v1/health/live")
def health_live():
    return {"data":{"status":"ok"}}

@router.get("/internal/v1/health/ready")
def health_ready():
    return {"data": {
                     "postgres": _up(_check_postgres),
                     "redis": _up(_check_redis),
                     "bucket": _up(_check_bucket),
                   }
           }