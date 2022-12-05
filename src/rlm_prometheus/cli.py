"""Command-line functions / entry points."""

import sys
from time import sleep

import click
from loguru import logger as log
from prometheus_client import Info, start_http_server

from . import __version__
from .config import get_config_from_env, load_config_file
from .metrics import RlmProductMetrics


def configure_logging(verbose: int):
    """Configure loguru logging / change log level.

    Parameters
    ----------
    verbose : int
        The desired log level, 0=WARNING (do not change the logger config),
        1=INFO, 2=DEBUG, 3=TRACE. Higher values will map to TRACE.
    """
    level = "WARNING"
    if verbose == 1:
        level = "INFO"
    elif verbose == 2:
        level = "DEBUG"
    elif verbose >= 3:
        level = "TRACE"
    # set up logging, loguru requires us to remove the default handler and
    # re-add a new one with the desired log-level:
    log.remove()
    log.add(sys.stderr, level=level)
    log.info(f"Set logging level to [{level}] ({verbose}).")


@click.command(help="Run the RLM metrics collector and exporter.")
@click.option("--config", type=str, help="A YAML configuration file.")
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase logging verbosity, may be repeated up to 3 times.",
)
def run_rlm_exporter(verbose, config):
    """Main CLI entry point for the RLM exporter. Blocking.

    Parameters
    ----------
    verbose : int
        Verbosity level for logging, ranges from 0 ("WARNING") to 3 ("TRACE").
    config : str
        A path to a configuration file. If `None` the settings will be derived
        from environment variables.
    """
    # do a first logging configuration to respect the command line parameters:
    configure_logging(verbose)

    if config:
        configuration = load_config_file(config)
    else:
        configuration = get_config_from_env()

    # verbosity might have been specified in the config / environment:
    if configuration.verbosity > verbose:
        configure_logging(configuration.verbosity)

    start_http_server(configuration.exporter_port)
    log.success(f"Providing metrics via HTTP on port {configuration.exporter_port}.")
    metrics = RlmProductMetrics(configuration)

    info = Info(
        name="rlm_exporter",
        documentation="Information on the RLM metrics collector and exporter service",
    )
    info.info(
        {
            "version": __version__,
            "collection_interval": f"{configuration.interval}s",
        }
    )

    log.success(
        f"{__package__} {__version__} started, "
        f"collection interval {configuration.interval}s."
    )

    while True:
        log.trace("Updating pool status...")
        try:
            metrics.update_metrics()
        except Exception as err:  # pylint: disable-msg=broad-except
            log.error(f"Updating metrics failed: {err}")
        sleep(configuration.interval)
