"""Configuration loader function(s)."""

import os
from box import Box


def load_config_file(filename):
    """Assemble a config object by loading values from a file."""
    config = Box.from_yaml(filename=filename)
    if "rlm_port" not in config.keys():
        config.rlm_port = "5054"
    if "rlm_host" not in config.keys():
        config.rlm_host = "localhost"
    if "exporter_port" not in config.keys():
        config.exporter_port = "8909"
    if "interval" not in config.keys():
        config.interval = 60
    if "isv" not in config.keys():
        raise ValueError("Config is missing setting for 'isv'!")
    return config


def get_config_from_env():
    """Assemble a config object from envrionment variables."""
    try:
        isv = os.environ["RLM_ISV"]
    except Exception as err:
        raise KeyError("Error getting configuration values:", err) from err

    rlm_host = os.environ.get("RLM_HOST", "localhost")
    rlm_port = os.environ.get("RLM_PORT", "5054")
    exporter_port = os.environ.get("RLM_EXPORTER_PORT", "8909")
    interval = os.environ.get("RLM_EXPORTER_INTERVAL", 60)

    return Box(
        {
            "rlm_port": rlm_port,
            "rlm_host": rlm_host,
            "exporter_port": exporter_port,
            "interval": interval,
            "isv": isv,
        }
    )
