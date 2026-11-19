
import json
from pathlib import Path
from uuid import uuid4

from jsonschema import Draft202012Validator, FormatChecker


# 1. Load Callback Schema
ROOT = Path(__file__).resolve().parents[1]

schema_path = ROOT / "contracts" / "callbacks.schema.json"

with open(schema_path, encoding="utf-8") as file:
    schema = json.load(file)

Draft202012Validator.check_schema(schema)


# 2. Create validator for each callback type
def make_validator(definition_name):
    selected_schema = {
        "$schema": schema["$schema"],
        "$defs": schema["$defs"],
        "$ref": f"#/$defs/{definition_name}"
    }

    return Draft202012Validator(
        selected_schema,
        format_checker=FormatChecker()
    )


# 3. Valid Progress Callback
progress_validator = make_validator("ProgressCallback")

valid_progress = {
    "job_id": str(uuid4()),
    "sequence": 1,
    "sent_at": "2026-11-19T10:00:00Z",
    "stage": "probe"
}

progress_validator.validate(valid_progress)
print("PASS: Valid Progress Callback accepted")


# 4. Invalid Progress Stage
invalid_progress = valid_progress.copy()
invalid_progress["stage"] = "upload"

errors = list(progress_validator.iter_errors(invalid_progress))

assert errors, "Invalid stage must be rejected"
print("PASS: Invalid Progress Stage rejected")


# 5. Valid Completed Callback
completed_validator = make_validator("CompletedCallback")

valid_completed = {
    "job_id": str(uuid4()),
    "sequence": 2,
    "sent_at": "2026-11-19T10:05:00Z",
    "media_info": {
        "duration_ms": 60000,
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "codec": "h264"
    }
}

completed_validator.validate(valid_completed)
print("PASS: Valid Completed Callback accepted")


# 6. Completed Callback without media_info
invalid_completed = valid_completed.copy()
del invalid_completed["media_info"]

errors = list(completed_validator.iter_errors(invalid_completed))

assert errors, "Missing media_info must be rejected"
print("PASS: Missing media_info rejected")


# 7. Valid Failed Callback
failed_validator = make_validator("FailedCallback")

valid_failed = {
    "job_id": str(uuid4()),
    "sequence": 3,
    "sent_at": "2026-11-19T10:06:00Z",
    "failed_stage": "index",
    "error": "MODELS_NOT_CONNECTED"
}

failed_validator.validate(valid_failed)
print("PASS: Valid Failed Callback accepted")


# 8. Valid Clip Status Callback
clip_validator = make_validator("ClipStatusCallback")

valid_clip = {
    "clip_job_id": str(uuid4()),
    "sequence": 1,
    "state": "ready",
    "clip_ref": "clips/video-123/0-5000-h264_720p.mp4"
}

clip_validator.validate(valid_clip)
print("PASS: Valid Clip Status accepted")


# 9. Invalid Clip State
invalid_clip = valid_clip.copy()
invalid_clip["state"] = "running"

errors = list(clip_validator.iter_errors(invalid_clip))

assert errors, "Invalid clip state must be rejected"
print("PASS: Invalid Clip State rejected")


# 10. Valid Acknowledgement Response
ack_validator = make_validator("AckEnvelope")

valid_ack = {
    "data": {
        "accepted": True,
        "duplicate": False
    }
}

ack_validator.validate(valid_ack)
print("PASS: Valid Ack Response accepted")
