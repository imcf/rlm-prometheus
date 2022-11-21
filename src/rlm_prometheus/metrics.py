from loguru import logger as log
from prometheus_client import Gauge

from .collector import LicProcessCollector


class RlmProductMetrics:
    def __init__(self, config, isv):
        self.config = config
        self.isv = isv
        self.collector = LicProcessCollector(config, isv)
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
        log.debug("Updating metrics...")
        tables = self.collector.collect()
        for _, row in tables[1].iterrows():
            product = row["Product"]
            if "imarisreader" in product:
                continue  # ignore readers
            for name, gauge in self.gauges.items():
                try:
                    value = float(row[name])
                except:  # pylint: disable-msg=bare-except
                    continue  # ignore anything that doesn't have a proper value
                gauge.labels(self.isv, product).set(value)
