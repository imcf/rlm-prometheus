"""Metrics collection classes."""

import pandas as pd
import requests
from loguru import logger as log

from prometheus_client import Summary


HTTP_REQUEST_TIME = Summary(
    "rlm_request_response_seconds", "time spent waiting for RLM to return data"
)
HTML_PARSING_TIME = Summary(
    "rlm_parse_data_seconds", "time spent parsing data from the RLM response"
)


@HTTP_REQUEST_TIME.time()
def send_http_request(url, data, timeout):
    """Wrapper for sending (and timing) an HTTP POST request.

    Parameters are identical to those of `requests.post()` with the same names.

    Exceptions are silenced into log messages as they shouldn't be passed on
    when running in service mode.

    Returns
    -------
    str or None
        The `text` property of the response object created by the `post()` call
        or `None` in case the call raised an exception.
    """
    try:
        response = requests.post(url=url, data=data, timeout=timeout)
    except Exception as err:  # pylint: disable-msg=broad-except
        log.error(f"Failed fetching data from RLM: {err}")
        return None

    return response.text


@HTML_PARSING_TIME.time()
def parse_html_into_dataframes(html, header):
    """Wrapper for parsing the RLM data into a dataframe (and timing it).

    Exceptions are silenced into log messages as they shouldn't be passed on
    when running in service mode.

    Parameters
    ----------
    html : str
        The HTML containing the tables to be parsed by Pandas.
    header : int or list-like
        The row to use to make the column headers, passed on directly to the
        `read_html()` call.

    Returns
    -------
    list(pandas.DataFrame) or None
        A list of dataframe objects, one per table, or `None` in case parsing
        the data failed or the input was `None`.
    """
    if html is None:  # happens if the HTTP request failed
        return None
    try:
        tables = pd.read_html(html, header=header)
    except Exception as err:  # pylint: disable-msg=broad-except
        log.error(f"Failed parsing tables from HTML: {err}")
        return None

    return tables


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
        html = self.uri
        if html[0:4] == "http":  # it URI starts with 'http' request the data:
            html = send_http_request(url=self.uri, data=self.postdata, timeout=5)

        tables = parse_html_into_dataframes(html, header=0)

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
