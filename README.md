# 📊 RLM-Prometheus 📊

[Prometheus][1] exporter providing metrics from a Reprise License Manager (RLM)
instance.

Currently tested on [Debian Linux][4] only, but as it is based on pure
[CPython][5] it should potentially also work on Windows - YMMV.

## ⚙🔧 Installation ⚙🔧

Example installation on Debian / Ubuntu:

```bash
# required for creating Python virtualenvs:
apt update
apt install -y python3-venv

# create a virtualenv in /opt:
python3 -m venv /opt/rlm-prometheus

# update 'pip' and install the 'rlm-prometheus' package:
/opt/rlm-prometheus/bin/pip install --upgrade pip
/opt/rlm-prometheus/bin/pip install rlm-prometheus
```

## 🏃 Running in foreground mode 🏃

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

## 👟 Running as a service 👟

```bash
adduser --system rlmexporter
cp -v /opt/rlm-prometheus/lib/python*/site-packages/resources/systemd/rlm-prometheus.service  /etc/systemd/system/
systemctl daemon-reload
systemctl edit rlm-prometheus.service
```

The last command will open an editor with the override configuration of the
service's unit file. Add a section like this **at the top** of the override
file, with the bare minimum of setting `RLM_ISV` and most likely also `RLM_URI`.
For other options available check for the commented-out lines further down in
the unit file setting environment variables starting with `RLM_`. Please note
that on *Ubuntu 20.04* the `systemct edit` command will present you with an
empty file, so you will have to copy the respective lines from below or the
provided *central* unit file.

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
systemctl enable --now rlm-prometheus.service
journalctl --follow --unit rlm-prometheus
```

Open ports for the `rlm-prometheus` exporter:

```bash
SOURCE="any"  # <-- put an IP address here to restrict access more
ufw allow from $SOURCE to any port 8909
```

## 🔥🧱 Firewall settings for RLM on Windows 🔥🧱

For the metrics collection it is obviously necessary the exporter can gather
data from your RLM instance. The standard approach is to send requests to RLM's
built-in web server. By default access to it is blocked and those restrictions
should not be lifted more than necessary.

There is an example snippet in [Open-RlmFirewallPort.ps1][2] that demonstrates
how to adjust the Windows firewall so the collector's host IP address is allowed
to connect to RLM.

## 👾 CAUTION: memory leak in RLM 👾

Repeatedly requesting data (e.g. every 5 minutes) from RLM's built-in web server
has shown to increase its memory consumption in a linear fashion over time on
our side. This indicates a memory leak in RLM, which eventually made the license
service fail silently.

To avoid (or rather work around) this, we did set up a scheduled task on the
server hosting the RLM service that is restarting the service once a night while
also rotating its corresponding log files at the same time.

Example code on how to achieve this via PowerShell is provided in
[Restart-RlmService.ps1][6].

## 🆙 Upgrading 🆙

Assuming the exporter has been installed as described above, an upgrade to a
newer version could be done like this:

```bash
/opt/rlm-prometheus/bin/pip install --upgrade rlm-prometheus
# check the changelog for potentially new configuration settings, integrate them
# by calling `systemctl edit rlm-prometheus.service` if necessary and finally
# restart the service:
systemctl restart rlm-prometheus.service
```

[1]: https://prometheus.io/
[2]: resources/powershell/Open-RlmFirewallPort.ps1
[3]: resources/config-example.yaml
[4]: https://debian.org/
[5]: https://github.com/python/cpython
[6]: resources/powershell/Restart-RlmService.ps1
