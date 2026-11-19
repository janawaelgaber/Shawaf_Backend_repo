
import json
from pathlib import Path
from uuid import uuid4

from jsonschema import Draft202012Validator, FormatChecker


# ==================================================
# 1. Load Search Schema
# ==================================================

ROOT = Path(__file__).resolve().parents[1]
schema_path = ROOT / "contracts" / "search.schema.json"

with open(schema_path, encoding="utf-8") as file:
    schema = json.load(file)

Draft202012Validator.check_schema(schema)


# ==================================================
# 2. Validator Factory
# ==================================================

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


internal_validator = make_validator("SearchHit")
public_validator = make_validator("SearchResult")
request_validator = make_validator("InternalSearchRequest")
envelope_validator = make_validator("InternalSearchEnvelope")


# ==================================================
# 3. Helper For Invalid Cases
# ==================================================

def expect_invalid(validator, data, description):
    errors = list(validator.iter_errors(data))

    assert errors, f"Expected rejection: {description}"

    print(f"PASS: {description}")


# ==================================================
# Test 1: Valid Internal Search Hit
# ==================================================

video_id = str(uuid4())

internal_hit = {
    "video_id": video_id,
    "match_start_ms": 25000,
    "match_end_ms": 30000,
    "score": 0.85
}

internal_validator.validate(internal_hit)

print("PASS: Valid Internal Search Hit accepted")


# ==================================================
# Test 2: Valid Public Search Result
# ==================================================

public_result = {
    "result_id": str(uuid4()),
    "video_id": video_id,
    "match_start_ms": 25000,
    "match_end_ms": 30000,
    "playback_start_ms": 23000,
    "playback_end_ms": 32000,
    "rank": 1
}

public_validator.validate(public_result)

print("PASS: Valid Public Search Result accepted")


# ==================================================
# Test 3: Public Result Must Not Include Score
# ==================================================

invalid_public_result = public_result.copy()
invalid_public_result["score"] = 0.85

expect_invalid(
    public_validator,
    invalid_public_result,
    "Public Result with score rejected"
)


# ==================================================
# Test 4: Missing Rank
# ==================================================

missing_rank = public_result.copy()
del missing_rank["rank"]

expect_invalid(
    public_validator,
    missing_rank,
    "Missing rank rejected"
)


# ==================================================
# Test 5: Valid Internal Search Request
# ==================================================

valid_request = {
    "search_id": str(uuid4()),
    "organization_id": str(uuid4()),
    "query_text": "person wearing a red shirt",
    "authorized_video_ids": [video_id],
    "identity_reference": None,
    "include_tentative": True,
    "limit": 10
}

request_validator.validate(valid_request)

print("PASS: Valid Internal Search Request accepted")


# ==================================================
# Test 6: Invalid include_tentative
# ==================================================

invalid_request = valid_request.copy()
invalid_request["include_tentative"] = False

expect_invalid(
    request_validator,
    invalid_request,
    "Invalid include_tentative rejected"
)


# ==================================================
# Test 7: Valid Internal Search Envelope
# ==================================================

valid_envelope = {
    "data": {
        "hits": [internal_hit]
    }
}

envelope_validator.validate(valid_envelope)

print("PASS: Valid Internal Search Envelope accepted")


# ==================================================
# Test 8: Internal Hit Without Score
# ==================================================

invalid_envelope = {
    "data": {
        "hits": [
            {
                "video_id": video_id,
                "match_start_ms": 25000,
                "match_end_ms": 30000
            }
        ]
    }
}

expect_invalid(
    envelope_validator,
    invalid_envelope,
    "Internal Hit without score rejected"
)


# ==================================================
# Test 9: Public Result Must Not Include Search ID
# ==================================================

invalid_search_id_result = public_result.copy()
invalid_search_id_result["search_id"] = str(uuid4())

expect_invalid(
    public_validator,
    invalid_search_id_result,
    "Public Result with search_id rejected"
)


# ==================================================
# Final Summary
# ==================================================

print("\nSUCCESS: All 9 Search Schema tests passed!")
