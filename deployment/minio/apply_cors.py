import json
import os
from pathlib import Path

import boto3
from botocore.config import Config


def main() -> None:
    origin = os.environ.get("FRONTEND_ORIGIN", "").strip()
    if not origin:
        print("FRONTEND_ORIGIN is empty. Skipping bucket CORS setup.")
        return

    template_path = Path(__file__).with_name("cors.json")
    configuration = json.loads(template_path.read_text(encoding="utf-8"))
    configuration["CORSRules"][0]["AllowedOrigins"] = [origin]

    client = boto3.client(
        "s3",
        endpoint_url="http://minio:9000",
        region_name="us-east-1",
        config=Config(s3={"addressing_style": "path"}),
    )
    client.put_bucket_cors(
        Bucket="shawaf-media",
        CORSConfiguration=configuration,
    )
    print(f"Applied bucket CORS for {origin}")


if __name__ == "__main__":
    main()