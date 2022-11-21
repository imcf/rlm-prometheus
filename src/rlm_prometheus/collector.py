"""Metrics collection classes."""

import pandas as pd
import requests
from loguru import logger as log


class RlmCollector:
    def __init__(self, config):
        log.trace(f"Instantiating {self.__class__}...")
        self.base_uri = f"http://{config.rlm_host}:{config.rlm_port}"
        self.uri = None
        self.postdata = None
        log.debug(f"Using base URI: [{self.base_uri}]")

    def collect(self):
        """Request metrics from RLM and parse them into a dataframe.

        Returns
        -------
        list[DataFrame]
        """
        try:
            # response = requests.post(self.uri, data=self.postdata, timeout=5)
            # tables = pd.read_html(response.text, header=0)
            tables = pd.read_html("rlmstat_lic_process.html", header=0)
        except Exception as err:  # pylint: disable-msg=broad-except
            log.error(f"Failed to collect or parse RLM metrics: {err}")
            return None

        return tables


class LicProcessCollector(RlmCollector):
    def __init__(self, config):
        log.trace(f"Instantiating {self.__class__}...")
        super().__init__(config)
        self.uri = f"{self.base_uri}/goform/rlmstat_lic_process"
        self.postdata = {
            "isv": config.isv,
            "instance": "0",
            "host": "",
            "wb": "rlmstat_lic",
            "pool": "0",
            "password": "",
            "ok": "Refresh",
        }
