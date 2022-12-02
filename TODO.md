# Development ToDo List

- [x] filter on product names in `RlmProductMetrics.update_metrics()` should not
  be hard coded
- [x] report parsing status (errors) and timings (request, parsing, ...)
- [x] report metrics on individual license checkouts / reservations
- [x] mention RLM memory leak and suggested workaround by restarting the service
  through a scheduled task (provide an example PowerShell script)
- [ ] allow logging verbosity to be configured through an environment variable
  to make it adjustable from the systemd unit file (otherwise this would require
  the command line to be changed which can't be done in an override file)
