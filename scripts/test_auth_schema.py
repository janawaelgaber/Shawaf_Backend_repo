
import json
from pathlib import Path
from uuid import uuid4

from jsonschema import Draft202012Validator, FormatChecker


# 1. Load Auth Schema
ROOT = Path(__file__).resolve().parents[1]
schema_path = ROOT / "contracts" / "auth.schema.json"

with open(schema_path, encoding="utf-8") as file:
    schema = json.load(file)

Draft202012Validator.check_schema(schema)


# 2. Create a validator for any definition
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


login_validator = make_validator("LoginRequest")
login_data_validator = make_validator("LoginData")


# Test 1: Valid Login Request
valid_login = {
    "email": "user@example.com",
    "password": "ExamplePassword123"
}

login_validator.validate(valid_login)
print("PASS: Valid Login Request accepted")


# Test 2: Invalid Email
invalid_login = valid_login.copy()
invalid_login["email"] = "wrong-email"

errors = list(login_validator.iter_errors(invalid_login))

assert errors, "Invalid email must be rejected"
print("PASS: Invalid email rejected")


# Test 3: Valid Login Data
valid_login_data = {
    "access_token": "example-access-token",
    "token_type": "Bearer",
    "expires_in": 900,
    "user": {
        "id": str(uuid4()),
        "email": "user@example.com",
        "full_name": "Test User",
        "is_platform_admin": False,
        "organization": {
            "id": str(uuid4()),
            "name": "Test Company"
        },
        "role": "investigator",
        "permissions": [
            "videos.read",
            "search.run"
        ]
    }
}

login_data_validator.validate(valid_login_data)
print("PASS: Valid Login Data accepted")


# Test 4: Missing Access Token
invalid_login_data = valid_login_data.copy()
del invalid_login_data["access_token"]

errors = list(login_data_validator.iter_errors(invalid_login_data))

assert errors, "Missing access_token must be rejected"
print("PASS: Missing access_token rejected")
