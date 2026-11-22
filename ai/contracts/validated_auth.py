
from typing import Literal
from uuid import UUID

from pydantic import Field

from .models.auth import (
    Organization as GeneratedOrganization,
    Me as GeneratedMe,
    LoginData as GeneratedLoginData,
    LoginResponse as GeneratedLoginResponse,
)


class Organization(GeneratedOrganization):
    id: UUID = Field(default=None)
    name: str = Field(default=None)


class Me(GeneratedMe):
    organization: Organization | None

    # Explicitly represent JSON null as Python None.
    role: Literal[
        "org_admin",
        "investigator",
        "auditor",
    ] | None


class LoginData(GeneratedLoginData):
    user: Me


class LoginResponse(GeneratedLoginResponse):
    data: LoginData = Field(default=None)
