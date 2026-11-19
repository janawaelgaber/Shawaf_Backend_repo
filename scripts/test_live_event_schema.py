
import json
from pathlib import Path
from uuid import uuid4

from jsonschema import Draft202012Validator, FormatChecker


# 1. Load Live Event Schema
ROOT = Path(__file__).resolve().parents[1]

schema_path = ROOT / "contracts" / "live-event.schema.json"

with open(schema_path, encoding="utf-8") as file:
    schema = json.load(file)

Draft202012Validator.check_schema(schema)


# 2. Create validator
validator = Draft202012Validator(
    {
        "$schema": schema["$schema"],
        "$defs": schema["$defs"],
        "$ref": "#/$defs/LiveEventCallback"
    },
    format_checker=FormatChecker()
)


# Helper to verify rejected data
def expect_invalid(data, description):
    errors = list(validator.iter_errors(data))
    assert errors, f"Expected rejection: {description}"
    print(f"PASS: {description}")


# Test 1: Valid Live Event
valid_event = {
    "camera_id": str(uuid4()),
    "organization_id": str(uuid4()),
    "label": "fall",
    "score": 0.91,
    "external_event_id": "evt-123",
    "sequence": 1,
    "sent_at": "2026-11-19T15:00:00Z"
}

validator.validate(valid_event)
print("PASS: Valid Live Event accepted")


# Test 2: Invalid Event Label
invalid_label = valid_event.copy()
invalid_label["label"] = "unknown"

expect_invalid(
    invalid_label,
    "Invalid Event Label rejected"
)


# Test 3: Missing Required Field
missing_org = valid_event.copy()
del missing_org["organization_id"]

expect_invalid(
    missing_org,
    "Missing organization_id rejected"
)


# Test 4: Invalid Sequence
invalid_sequence = valid_event.copy()
invalid_sequence["sequence"] = 0

expect_invalid(
    invalid_sequence,
    "Sequence 0 rejected"
)


# Test 5: Invalid Camera UUID
invalid_uuid = valid_event.copy()
invalid_uuid["camera_id"] = "camera-123"

expect_invalid(
    invalid_uuid,
    "Invalid Camera UUID rejected"
)


# Test 6: Invalid Date-Time
invalid_date = valid_event.copy()
invalid_date["sent_at"] = "yesterday"

expect_invalid(
    invalid_date,
    "Invalid Date-Time rejected"
)


# Test 7: Invalid Score Type
invalid_score = valid_event.copy()
invalid_score["score"] = "high"

expect_invalid(
    invalid_score,
    "String Score rejected"
)


# Test 8: All Supported Event Labels
labels = [
    "fight",
    "fall",
    "running",
    "crowd_formation",
    "fire"
]

for label in labels:
    event = valid_event.copy()
    event["label"] = label
    validator.validate(event)

print("PASS: All 5 Event Labels accepted")
