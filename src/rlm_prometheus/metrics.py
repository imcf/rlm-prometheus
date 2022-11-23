"""Metrics for the RLM collector."""

from loguru import logger as log
from prometheus_client import Gauge

from .collector import LicProcessCollector


class RlmProductMetrics:

    """Product metrics class."""

    def __init__(self, config):
        self.config = config
        self.collector = LicProcessCollector(config)
        self.gauges = {
            "count": Gauge(
                name="rlm_product_count_total",
                documentation="total licenses in product pool",
                labelnames=["isv", "product"],
            ),
            "inuse": Gauge(
                name="rlm_product_inuse_total",
                documentation="licenses currently in use / checked out",
                labelnames=["isv", "product"],
            ),
        }

    def update_metrics(self):
        """Call the metrics collector and process the result."""
        log.debug("Updating metrics...")
        try:
            tables = self.collector.collect()
        except Exception as err:  # pylint: disable-msg=broad-except
            raise RuntimeError(f"Fetching new data failed: {err}") from err

        # in case no licenses are in use the returned data will only contain
        # one single table, otherwise it should have two:
        count = len(tables)
        if count == 1:
            pool_status = tables[0]
        elif count == 2:
            pool_status = tables[1]
        else:
            raise ValueError(
                f"Cannot parse data, found {count} tables - expected 1 or 2!"
            )

        for _, row in pool_status.iterrows():
            product = row["Product"]
            if "imarisreader" in product:
                continue  # ignore readers
            for name, gauge in self.gauges.items():
                try:
                    value = float(row[name])
                except:  # pylint: disable-msg=bare-except
                    continue  # ignore anything that doesn't have a proper value
                gauge.labels(self.config.isv, product).set(value)
