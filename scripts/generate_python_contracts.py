
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

COMMON = [
    "--input-file-type", "jsonschema",
    "--output-model-type", "pydantic_v2.BaseModel",
    "--target-python-version", "3.11",
    "--target-pydantic-version", "2",
    "--field-constraints",
    "--disable-timestamp",
]

CONTRACTS = [
    ("processing-job.schema.json", "processing_job.py",
     ["--class-name", "ProcessingJobRequest"]),

    ("auth.schema.json", "auth.py",
     ["--skip-root-model", "--strict-nullable"]),

    ("search.schema.json", "search.py",
     ["--skip-root-model", "--generate-schema-validators",
      "--schema-validator-type", "pydantic-v2"]),

    ("callbacks.schema.json", "callbacks.py",
     ["--skip-root-model"]),

    ("live-event.schema.json", "live_event.py",
     ["--skip-root-model"]),
]


def main():
    generator = shutil.which("datamodel-codegen")

    if not generator:
        print("ERROR: datamodel-codegen not found. Activate .venv.")
        sys.exit(1)

    output_dir = ROOT / "ai" / "contracts" / "models"
    output_dir.mkdir(parents=True, exist_ok=True)

    for schema, output, extra in CONTRACTS:
        command = [
            generator,
            "--input", str(ROOT / "contracts" / schema),
            "--output", str(output_dir / output),
            *COMMON,
            *extra,
        ]

        print(f"\nGenerating {output}...")
        subprocess.run(command, cwd=ROOT, check=True)
        print(f"PASS: {output}")

    print("\nAll Python contract models generated successfully.")


if __name__ == "__main__":
    main()
