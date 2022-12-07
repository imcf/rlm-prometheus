"""Metrics for the RLM collector."""

import re

from loguru import logger as log
from prometheus_client import Gauge

from .collector import LicProcessCollector


class RlmProductMetrics:

    """Product metrics class."""

    def __init__(self, config):
        log.trace(f"Instantiating {self.__class__}...")
        self.config = config
        self.collector = LicProcessCollector(config)
        self.pool_gauges = {
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
        self.ignoreproducts = config.get("ignoreproducts", None)
        if self.ignoreproducts:
            log.debug(f"Metrics will ignore products matching '{self.ignoreproducts}'.")
            self.ignoreproducts = re.compile(self.ignoreproducts)
        if self.config.checkout_details:
            self.license_gauges = {
                "# lic": Gauge(
                    name="rlm_license_checkout",
                    documentation="details on license checkouts",
                    labelnames=["isv", "product", "user", "hostname"],
                ),
                "# res": Gauge(
                    name="rlm_license_reservation",
                    documentation="details on license reservations",
                    labelnames=["isv", "product", "user", "hostname"],
                ),
            }
            log.success("Will report details on license checkouts in metrics.")

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
        process_checkouts = False
        if count == 1:
            log.trace("Parsed 1 table, assuming pool status data.")
            pool_status = tables[0]
        elif count == 2:
            log.trace("Parsed 2 tables, assuming license and pool status data.")
            pool_status = tables[1]
            if self.config.checkout_details:
                process_checkouts = True
                checkouts = tables[0]
        else:
            raise ValueError(
                f"Cannot parse data, found {count} tables - expected 1 or 2!"
            )

        for _, row in pool_status.iterrows():
            product = row["Product"]
            if self.ignoreproducts and self.ignoreproducts.findall(product):
                # log.trace(f"Ignoring product '{product}'...")
                continue
            log.trace(f"Processing pool status for product {product}...")
            for name, gauge in self.pool_gauges.items():
                try:
                    value = float(row[name])
                except:  # pylint: disable-msg=bare-except
                    continue  # ignore anything that doesn't have a proper value
                gauge.labels(self.config.isv, product).set(value)

        # this clearing is required as otherwise previous checkout values that
        # do not exist in the current response any more (because the license has
        # been returned) would still keep their old value:
        for name, gauge in self.license_gauges.items():
            log.trace(f"Clearing labelsets for gauge {name}...")
            gauge.clear()

        if not process_checkouts:
            log.trace("Not processing checkouts (not requested or none present).")
            return

        for _, row in checkouts.iterrows():
            product = row["Product"]
            if self.ignoreproducts and self.ignoreproducts.findall(product):
                # log.trace(f"Ignoring product '{product}'...")
                continue
            log.trace(f"Processing license status for product {product}...")
            for name, gauge in self.license_gauges.items():
                try:
                    user = row["user"]
                    host = row["host"]
                    value = float(row[name])
                except:  # pylint: disable-msg=bare-except
                    continue  # ignore anything that doesn't have a proper value
                gauge.labels(self.config.isv, product, user, host).set(value)
