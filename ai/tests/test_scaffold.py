import json

from ai.api.main import app
from ai.contracts.hmac import sign, vector_path
from ai.persistence.models import Base
from ai.workers.queues import QUEUES


def test_inference_app_starts():
    assert app.title == "SHAWAF inference"


def test_queues_match_the_tickets():
    assert QUEUES == ("pipeline.gpu", "pipeline.cpu", "media.clips", "callbacks")


def test_analytics_tables_have_no_cross_schema_names():
    names = {table.name for table in Base.metadata.tables.values()}
    assert names == {
        "jobs",
        "runs",
        "outbox_callbacks",
        "live_cameras",
        "search_calls",
        "clip_jobs",
    }
    assert "state" not in Base.metadata.tables["analytics.jobs"].columns
    assert "processing_run_id" not in Base.metadata.tables["analytics.jobs"].columns
    assert "processing_run_id" not in Base.metadata.tables["analytics.clip_jobs"].columns


def test_hmac_vector_signs():
    vector = json.loads(vector_path().read_text(encoding="utf-8"))
    signature = sign(
        vector["secret"],
        vector["timestamp"],
        vector["method"],
        vector["path"],
        vector["raw_body"].encode(),
    )
    assert len(signature) == 64


def test_repo_tree_matches_scrum_120():
    import subprocess
    import sys
    from pathlib import Path

    script = Path(__file__).resolve().parents[2] / "scripts" / "repo_tree.py"
    result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
