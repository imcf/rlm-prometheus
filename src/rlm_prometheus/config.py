"""Configuration loader function(s)."""

import os
from box import Box


def load_config_file(filename):
    """Assemble a config object by loading values from a file."""
    raise NotImplementedError


def get_config_from_env():
    """Assemble a config object from envrionment variables."""
    try:
        isv = os.environ["RLM_ISV"]
    except Exception as err:
        raise KeyError("Error getting configuration values:", err) from err

    rlm_host = os.environ.get("RLM_HOST", "localhost")
    rlm_port = os.environ.get("RLM_PORT", "5054")
    exporter_port = os.environ.get("RLM_PORT", "8909")

    return Box(
        {
            "rlm_port": rlm_port,
            "rlm_host": rlm_host,
            "exporter_port": exporter_port,
            "isv": isv,
        }
    )
