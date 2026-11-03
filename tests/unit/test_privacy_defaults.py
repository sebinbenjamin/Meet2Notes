from __future__ import annotations

import json
import os
import subprocess
import sys

DEFAULTS = {
    "LITELLM_LOCAL_MODEL_COST_MAP": "True",
    "PYANNOTE_METRICS_ENABLED": "0",
    "HF_HUB_DISABLE_TELEMETRY": "1",
    "DO_NOT_TRACK": "1",
}


def _env_after_import(extra: dict[str, str]) -> dict[str, str | None]:
    """Import the package in a fresh interpreter and report the resulting values."""
    env = {key: value for key, value in os.environ.items() if key not in DEFAULTS}
    env.update(extra)
    script = (
        "import json, os, local_meeting_ai; "
        f"print(json.dumps({{name: os.environ.get(name) for name in {list(DEFAULTS)!r}}}))"
    )
    result = subprocess.run(
        [sys.executable, "-c", script], env=env, capture_output=True, text=True, check=True
    )
    return json.loads(result.stdout)


def test_importing_the_package_opts_out_of_telemetry() -> None:
    assert _env_after_import({}) == DEFAULTS


def test_explicit_environment_values_win() -> None:
    assert _env_after_import({"PYANNOTE_METRICS_ENABLED": "1"})["PYANNOTE_METRICS_ENABLED"] == "1"
