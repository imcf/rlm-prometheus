"""Metrics collection classes."""

import pandas as pd
import requests
from loguru import logger as log


class RlmCollector:

    """Abstract base collector class."""

    def __init__(self, config):
        # log.trace(f"Instantiating {self.__class__}...")
        self.base_uri = f"{config.rlm_uri}"
        log.debug(f"Using base URI: [{self.base_uri}]")
        self._uri = None
        self.postdata = None

    @property
    def uri(self):
        """Getter method for the `uri` attribute.

        Raises
        ------
        TypeError
            Raised in case the `uri` attribute is set to `None`.
        """
        if self._uri is None:
            raise TypeError("Instance doesn't have its `uri` attribute set!")
        return self._uri

    def set_stats_name(self, value):
        """Set name of the stats to request and process.

        This method actually sets the `uri` instance attribute depending on the
        `rlm_uri` configuration value.

        Parameters
        ----------
        value : str
            The name of the stats to request from RLM, e.g. `rlmstat_lic_process`.
        """
        if self.base_uri[0:5] == "http:":
            full_uri = f"{self.base_uri}/goform/{value}"
        else:
            full_uri = f"{self.base_uri}/{value}.html"
        log.trace(f"Setting `uri` value of {self.__class__} to [{full_uri}]...")
        self._uri = full_uri

    def collect(self):
        """Request metrics from RLM and parse them into a dataframe.

        Returns
        -------
        list[DataFrame]
        """
        log.trace(f"Collecting data from [{self.uri}]...")
        try:
            html = self.uri
            if html[0:4] == "http":  # it URI starts with 'http' request the data:
                response = requests.post(self.uri, data=self.postdata, timeout=5)
                html = response.text

            tables = pd.read_html(html, header=0)
        except Exception as err:  # pylint: disable-msg=broad-except
            log.error(f"Failed to collect or parse RLM metrics: {err}")
            return None

        return tables


class LicProcessCollector(RlmCollector):

    """Collector for "lic_process" data."""

    def __init__(self, config):
        log.trace(f"Instantiating {self.__class__}...")
        super().__init__(config)
        self.set_stats_name("rlmstat_lic_process")
        self.postdata = {
            "isv": config.isv,
            "instance": "0",
            "host": "",
            "wb": "rlmstat_lic",
            "pool": "0",
            "password": "",
            "ok": "Refresh",
        }
