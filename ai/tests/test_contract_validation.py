
import pytest
from jsonschema.exceptions import ValidationError as SchemaError

from ai.contracts.validation import validate_contract

from ai.contracts.models.processing_job import ProcessingJobRequest
from ai.contracts.models.auth import LoginRequest
from ai.contracts.validated_auth import Me, LoginResponse
from ai.contracts.models.search import (
    InternalSearchRequest,
    InternalSearchEnvelope,
)
from ai.contracts.validated_models import PublicSearchResult
from ai.contracts.models.callbacks import (
    ProgressCallback,
    CompletedCallback,
    FailedCallback,
    ClipStatusCallback,
    AckEnvelope,
)
from ai.contracts.models.live_event import LiveEventCallback


UUID1 = "550e8400-e29b-41d4-a716-446655440000"
UUID2 = "550e8400-e29b-41d4-a716-446655440001"
UUID3 = "550e8400-e29b-41d4-a716-446655440002"
UUID4 = "550e8400-e29b-41d4-a716-446655440003"

TIMESTAMP = "2026-11-22T01:20:00Z"


def validate(schema, payload, model, definition=None):
    return validate_contract(schema, payload, model, definition)


# =====================================================
# 1. PROCESSING JOB
# =====================================================

JOB = {
    "job_id": UUID1,
    "organization_id": UUID2,
    "video_id": UUID3,
    "camera_id": UUID4,
    "media_ref": "videos/sample.mp4",
    "content_type": "video/mp4",
    "size_bytes": 1024,
    "pipeline_version": "v1",
    "attempt": 1,
    "requested_at": TIMESTAMP,
}


def test_processing_job_valid():
    result = validate(
        "processing-job", JOB, ProcessingJobRequest
    )
    assert result.attempt == 1


def test_processing_job_optional_nullable_field():
    result = validate(
        "processing-job",
        {**JOB, "recorded_start_utc": None},
        ProcessingJobRequest,
    )
    assert result.recorded_start_utc is None


def test_processing_job_rejects_string_integer():
    with pytest.raises(SchemaError):
        validate(
            "processing-job",
            {**JOB, "size_bytes": "1024"},
            ProcessingJobRequest,
        )


def test_processing_job_rejects_zero_attempt():
    with pytest.raises(SchemaError):
        validate(
            "processing-job",
            {**JOB, "attempt": 0},
            ProcessingJobRequest,
        )


def test_processing_job_rejects_invalid_uuid():
    with pytest.raises(SchemaError):
        validate(
            "processing-job",
            {**JOB, "job_id": "invalid-uuid"},
            ProcessingJobRequest,
        )


# =====================================================
# 2. AUTH
# =====================================================

def test_auth_valid_login_request():
    result = validate(
        "auth",
        {"email": "ahmed@example.com", "password": "secret"},
        LoginRequest,
        "LoginRequest",
    )
    assert str(result.email) == "ahmed@example.com"


def test_auth_rejects_invalid_email():
    with pytest.raises(SchemaError):
        validate(
            "auth",
            {"email": "not-an-email", "password": "secret"},
            LoginRequest,
            "LoginRequest",
        )


def test_auth_rejects_empty_password():
    with pytest.raises(SchemaError):
        validate(
            "auth",
            {"email": "ahmed@example.com", "password": ""},
            LoginRequest,
            "LoginRequest",
        )


ME = {
    "id": UUID1,
    "email": "ahmed@example.com",
    "full_name": "Ahmed",
    "is_platform_admin": False,
    "organization": None,
    "role": None,
    "permissions": ["org.read"],
}


def test_auth_me_accepts_nullable_fields():
    result = validate("auth", ME, Me, "Me")
    assert result.organization is None
    assert result.role is None


def test_auth_me_accepts_optional_organization_fields():
    result = validate(
        "auth",
        {**ME, "organization": {}},
        Me,
        "Me",
    )
    assert result.organization is not None


def test_auth_rejects_null_organization_id():
    with pytest.raises(SchemaError):
        validate(
            "auth",
            {
                **ME,
                "organization": {"id": None},
            },
            Me,
            "Me",
        )


def test_auth_login_response_data_is_optional():
    validate("auth", {}, LoginResponse, "LoginResponse")


def test_auth_login_response_rejects_null_data():
    with pytest.raises(SchemaError):
        validate(
            "auth",
            {"data": None},
            LoginResponse,
            "LoginResponse",
        )


# =====================================================
# 3. SEARCH
# =====================================================

SEARCH_REQUEST = {
    "search_id": UUID1,
    "organization_id": UUID2,
    "query_text": "person wearing red",
    "authorized_video_ids": [UUID3],
    "identity_reference": None,
    "include_tentative": True,
    "limit": 10,
}


def test_search_valid_internal_request():
    result = validate(
        "search",
        SEARCH_REQUEST,
        InternalSearchRequest,
        "InternalSearchRequest",
    )
    assert result.include_tentative.value is True


def test_search_rejects_include_tentative_false():
    with pytest.raises(SchemaError):
        validate(
            "search",
            {**SEARCH_REQUEST, "include_tentative": False},
            InternalSearchRequest,
            "InternalSearchRequest",
        )


def test_search_rejects_zero_limit():
    with pytest.raises(SchemaError):
        validate(
            "search",
            {**SEARCH_REQUEST, "limit": 0},
            InternalSearchRequest,
            "InternalSearchRequest",
        )


def test_search_valid_internal_envelope():
    payload = {
        "data": {
            "hits": [
                {
                    "video_id": UUID3,
                    "match_start_ms": 100,
                    "match_end_ms": 200,
                    "score": 0.95,
                }
            ]
        }
    }

    validate(
        "search",
        payload,
        InternalSearchEnvelope,
        "InternalSearchEnvelope",
    )


PUBLIC_RESULT = {
    "result_id": UUID1,
    "video_id": UUID2,
    "match_start_ms": 100,
    "match_end_ms": 200,
    "playback_start_ms": 50,
    "playback_end_ms": 300,
    "rank": 1,
}


def test_search_valid_public_result():
    validate(
        "search",
        PUBLIC_RESULT,
        PublicSearchResult,
        "SearchResult",
    )


@pytest.mark.parametrize("field", ["score", "search_id"])
def test_search_rejects_internal_fields_in_public_result(field):
    with pytest.raises(SchemaError):
        validate(
            "search",
            {**PUBLIC_RESULT, field: "unexpected"},
            PublicSearchResult,
            "SearchResult",
        )


# =====================================================
# 4. CALLBACKS
# =====================================================

PROGRESS = {
    "job_id": UUID1,
    "sequence": 1,
    "sent_at": TIMESTAMP,
    "stage": "probe",
}


def test_callback_valid_progress():
    validate(
        "callbacks", PROGRESS, ProgressCallback, "ProgressCallback"
    )


def test_callback_rejects_invalid_stage():
    with pytest.raises(SchemaError):
        validate(
            "callbacks",
            {**PROGRESS, "stage": "unknown"},
            ProgressCallback,
            "ProgressCallback",
        )


def test_callback_rejects_zero_sequence():
    with pytest.raises(SchemaError):
        validate(
            "callbacks",
            {**PROGRESS, "sequence": 0},
            ProgressCallback,
            "ProgressCallback",
        )


def test_callback_valid_completed():
    payload = {
        "job_id": UUID1,
        "sequence": 2,
        "sent_at": TIMESTAMP,
        "media_info": {
            "duration_ms": 10000,
            "width": 1920,
            "height": 1080,
            "fps": 30.0,
            "codec": "h264",
        },
    }

    validate(
        "callbacks", payload, CompletedCallback, "CompletedCallback"
    )


def test_callback_rejects_missing_media_info():
    with pytest.raises(SchemaError):
        validate(
            "callbacks",
            {
                "job_id": UUID1,
                "sequence": 2,
                "sent_at": TIMESTAMP,
            },
            CompletedCallback,
            "CompletedCallback",
        )


def test_callback_valid_failed():
    payload = {
        "job_id": UUID1,
        "sequence": 3,
        "sent_at": TIMESTAMP,
        "failed_stage": "index",
        "error": "Processing failed",
    }

    validate(
        "callbacks", payload, FailedCallback, "FailedCallback"
    )


def test_callback_valid_clip_status():
    payload = {
        "clip_job_id": UUID1,
        "sequence": 1,
        "state": "ready",
        "clip_ref": None,
    }

    validate(
        "callbacks",
        payload,
        ClipStatusCallback,
        "ClipStatusCallback",
    )


def test_callback_rejects_invalid_clip_state():
    payload = {
        "clip_job_id": UUID1,
        "sequence": 1,
        "state": "processing",
    }

    with pytest.raises(SchemaError):
        validate(
            "callbacks",
            payload,
            ClipStatusCallback,
            "ClipStatusCallback",
        )


def test_callback_valid_ack_envelope():
    payload = {
        "data": {
            "accepted": True,
            "duplicate": False,
        }
    }

    validate("callbacks", payload, AckEnvelope, "AckEnvelope")


# =====================================================
# 5. LIVE EVENTS
# =====================================================

EVENT = {
    "camera_id": UUID1,
    "organization_id": UUID2,
    "label": "fight",
    "score": 0.95,
    "external_event_id": "event-001",
    "sequence": 1,
    "sent_at": TIMESTAMP,
}


@pytest.mark.parametrize(
    "label",
    ["fight", "fall", "running", "crowd_formation", "fire"],
)
def test_live_event_valid_labels(label):
    validate(
        "live-event",
        {**EVENT, "label": label},
        LiveEventCallback,
        "LiveEventCallback",
    )


def test_live_event_rejects_invalid_label():
    with pytest.raises(SchemaError):
        validate(
            "live-event",
            {**EVENT, "label": "unknown"},
            LiveEventCallback,
            "LiveEventCallback",
        )


def test_live_event_rejects_string_score():
    with pytest.raises(SchemaError):
        validate(
            "live-event",
            {**EVENT, "score": "0.95"},
            LiveEventCallback,
            "LiveEventCallback",
        )


def test_live_event_accepts_integer_score():
    result = validate(
        "live-event",
        {**EVENT, "score": 1},
        LiveEventCallback,
        "LiveEventCallback",
    )
    assert result.score == 1


def test_live_event_rejects_zero_sequence():
    with pytest.raises(SchemaError):
        validate(
            "live-event",
            {**EVENT, "sequence": 0},
            LiveEventCallback,
            "LiveEventCallback",
        )


def test_live_event_rejects_invalid_timestamp():
    with pytest.raises(SchemaError):
        validate(
            "live-event",
            {**EVENT, "sent_at": "not-a-date"},
            LiveEventCallback,
            "LiveEventCallback",
        )
