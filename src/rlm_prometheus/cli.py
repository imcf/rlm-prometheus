"""Command-line functions / entry points."""

from time import sleep

from loguru import logger as log
from prometheus_client import start_http_server

from .config import get_config_from_env
from .metrics import RlmProductMetrics


def run_exporter():
    config = get_config_from_env()
    start_http_server(config.exporter_port)
    metrics = RlmProductMetrics(config, isv="bitplane")
    while True:
        log.trace("Updating pool status...")
        try:
            metrics.collector.collect()
        except Exception as err:  # pylint: disable-msg=broad-except
            log.error(f"Collecting new data failed: {err}")
        try:
            metrics.update_metrics()
        except Exception as err:  # pylint: disable-msg=broad-except
            log.error(f"Updating metrics failed: {err}")
        sleep(60)
