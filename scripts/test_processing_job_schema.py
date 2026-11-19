
import json
from pathlib import Path
from uuid import uuid4

from jsonschema import Draft202012Validator, FormatChecker

# Load our schema
ROOT = Path(__file__).resolve().parents[1]
schema_path = ROOT / "contracts" / "processing-job.schema.json"

with open(schema_path, encoding="utf-8") as file:
    schema = json.load(file)

# Check that the schema itself is valid
Draft202012Validator.check_schema(schema)

# Create validator
validator = Draft202012Validator(
    schema,
    format_checker=FormatChecker()
)

# Test 1: Valid request
video_id = str(uuid4())

valid_job = {
    "job_id": str(uuid4()),
    "organization_id": str(uuid4()),
    "video_id": video_id,
    "camera_id": str(uuid4()),
    "media_ref": f"videos/{video_id}/original.mp4",
    "content_type": "video/mp4",
    "size_bytes": 18432000,
    "recorded_start_utc": None,
    "pipeline_version": "v1",
    "attempt": 1,
    "requested_at": "2026-11-19T10:00:00Z"
}

validator.validate(valid_job)
print("PASS: Valid request accepted")

# Test 2: Invalid attempt type
invalid_job = valid_job.copy()
invalid_job["attempt"] = "first"

errors = list(validator.iter_errors(invalid_job))
assert errors, "Invalid attempt should be rejected"

print("PASS: Invalid attempt rejected")
for error in errors:
    print("Reason:", error.message)

# Test 3: Missing required field
missing_field_job = valid_job.copy()
del missing_field_job["video_id"]

errors = list(validator.iter_errors(missing_field_job))
assert errors, "Missing video_id should be rejected"

print("PASS: Missing required field rejected")

# Test 4: Invalid UUID
invalid_uuid_job = valid_job.copy()
invalid_uuid_job["video_id"] = "hello"

errors = list(validator.iter_errors(invalid_uuid_job))
assert errors, "Invalid UUID should be rejected"

print("PASS: Invalid UUID rejected")


# Test 5: Invalid date-time
invalid_date_job = valid_job.copy()
invalid_date_job["requested_at"] = "yesterday"

errors = list(validator.iter_errors(invalid_date_job))
assert errors, "Invalid date-time should be rejected"

print("PASS: Invalid date-time rejected")


# Test 6: Optional field omitted
optional_job = valid_job.copy()
del optional_job["recorded_start_utc"]

validator.validate(optional_job)

print("PASS: Optional field can be omitted")


# Test 7: Optional field is null
null_job = valid_job.copy()
null_job["recorded_start_utc"] = None

validator.validate(null_job)

print("PASS: Optional field accepts null")
