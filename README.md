# RLM-Prometheus

[Prometheus][1] exporter providing metrics from a Reprise License Manager (RLM)
instance.

## Installation

Example installation on Debian / Ubuntu:

```bash
# required for creating Python virtualenvs:
apt install python3-venv

# create a virtualenv in /opt:
python3 -m venv /opt/rlm-exporter

# update 'pip' and install the 'rlm-exporter' package:
/opt/rlm-exporter/bin/pip install --upgrade pip
/opt/rlm-exporter/bin/pip install rlm-exporter
```

## Running in foreground mode

This is mostly relevant for testing configuration settings and checking if the
exporter works as expected - to do this either activate the previously created
Python environment or call the `rlm_exporter` script using the full path to that
environment.

For convenience it is reasonable to use a configuration file in such a situation
instead of setting all the environment variables manually. Simply copy the
[config-example.yaml][3] file to e.g. `config.yaml` and adjust the settings
there. Then run the exporter like this:

```bash
rlm_exporter -vvv --config config.yaml
```

The exporter running in foreground can be terminated as usual via `Ctrl+C`.

## Running as a service

```bash
adduser --system rlmexporter
cp -v /opt/rlm-exporter/lib/python*/site-packages/resources/systemd/rlm-exporter.service  /etc/systemd/system/
systemctl daemon-reload
systemctl edit rlm-exporter.service
```

The last command will open an editor with the override configuration of the
service's unit file. Add a section like this **at the top** of the override
file, with the bare minimum of setting `RLM_ISV` and most likely also `RLM_URI`.
For other options available check for the commented-out lines further down in
the unit file setting environment variables starting with `RLM_`.

```text
[Service]
### specific configuration for the RLM exporter service:
Environment=RLM_ISV=example_isv
Environment=RLM_URI=http://license-server.example.xy:5054
```

Finally enable the service and start it right away. The second line will show
the log messages on the console until `Ctrl+C` is pressed. This way you should
be able to tell if the service has started up properly and is providing metrics
on the configured port:

```bash
systemctl enable --now rlm-exporter.service
journalctl --follow --unit rlm-exporter
```

## Firewall settings for RLM on Windows

For the metrics collection it is obviously necessary the exporter can gather data from
your RLM instance. The standard approach is to send requests to RLM's built-in web
server. By default access to it is blocked and those restrictions should not be lifted
more than necessary.

There is an example snippet in [Open-RlmFirewallPort.ps1][2] that demonstrates how to
adjust the Windows firewall so the collector's host IP address is allowed to connect
to RLM.

[1]: https://prometheus.io/
[2]: resources/powershell/Open-RlmFirewallPort.ps1
[3]: resources/config-example.yaml
