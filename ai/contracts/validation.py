
from functools import lru_cache
from pathlib import Path
import json
from typing import TypeVar

from jsonschema import Draft202012Validator, FormatChecker
from pydantic import BaseModel


ModelT = TypeVar("ModelT", bound=BaseModel)

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "contracts"

ALLOWED_SCHEMAS = {
    "processing-job",
    "search",
    "auth",
    "callbacks",
    "live-event",
}


@lru_cache(maxsize=None)
def load_schema(schema_name: str) -> dict:
    if schema_name not in ALLOWED_SCHEMAS:
        raise ValueError(f"Unknown contract: {schema_name}")

    path = SCHEMA_DIR / f"{schema_name}.schema.json"

    with path.open("r", encoding="utf-8") as file:
        schema = json.load(file)

    Draft202012Validator.check_schema(schema)

    return schema


@lru_cache(maxsize=None)
def get_validator(schema_name: str, definition: str | None = None):
    schema = load_schema(schema_name)

    if definition is not None:
        definitions = schema.get("$defs", {})

        if definition not in definitions:
            raise ValueError(
                f"Unknown definition '{definition}' "
                f"in {schema_name}"
            )

        schema = {
            "$schema": schema["$schema"],
            "$ref": f"#/$defs/{definition}",
            "$defs": definitions,
        }

    return Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )


def validate_contract(
    schema_name: str,
    payload: dict,
    model: type[ModelT],
    definition: str | None = None,
) -> ModelT:

    validator = get_validator(schema_name, definition)

    # Validate against the original JSON Schema first.
    validator.validate(payload)

    # Convert the validated payload into a Pydantic model.
    return model.model_validate(payload)
