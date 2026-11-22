
from collections.abc import Mapping
from typing import Any

from pydantic import model_validator

from .models.search import SearchResult as GeneratedSearchResult


class PublicSearchResult(GeneratedSearchResult):

    @model_validator(mode="before")
    @classmethod
    def reject_internal_only_fields(cls, value: Any) -> Any:
        if isinstance(value, Mapping):
            forbidden = {"score", "search_id"}.intersection(value)

            if forbidden:
                fields = ", ".join(sorted(forbidden))
                raise ValueError(
                    f"Public Search Result cannot contain: {fields}"
                )

        return value
