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

## Running as a service

```bash
adduser --system rlmexporter
cp -v /opt/rlm-exporter/lib/python*/site-packages/resources/systemd/rlm-exporter.service  /etc/systemd/system/
systemctl daemon-reload
systemctl edit rlm-exporter.service
```

The last command will open an editor with the override configuration of the
service's unit file. Add a section like this **at the top** of the override
file, with the bare minimum of setting `RLM_ISV` and most likely also `RLM_URI`:

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
