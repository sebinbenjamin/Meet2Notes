"""Meet2Notes application package."""

import os

__version__ = "0.9.0"

# Opt out of third-party telemetry and remote lookups before any dependency is
# imported. Each uses setdefault, so an explicit environment value still wins.
#   LiteLLM fetches its model price list from GitHub on import.
#   pyannote.audio sends usage metrics to otel.pyannote.ai by default.
#   huggingface_hub adds telemetry to its user agent; DO_NOT_TRACK covers others.
for _name, _value in {
    "LITELLM_LOCAL_MODEL_COST_MAP": "True",
    "PYANNOTE_METRICS_ENABLED": "0",
    "HF_HUB_DISABLE_TELEMETRY": "1",
    "DO_NOT_TRACK": "1",
}.items():
    os.environ.setdefault(_name, _value)
del _name, _value
