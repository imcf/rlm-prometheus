# Changelog

## 0.2.1

* Fixes a bug where returned licenses were incorrectly still reported as
  *checked-out* or *reserved* in the `rlm_license_checkout` and
  `rlm_license_reservation` gauges.

## 0.2.0

* Optionally report metrics on individual license checkouts / reservations.
  Requires new configuration setting `RLM_CHECKOUT_DETAILS` (environment) /
  `checkout_details` (file) to be switched on.
* New configuration setting `RLM_IGNORE_PRODUCTS` (environment) /
  `ignoreproducts` (file) to supply a regular expression for product names that
  should be ignored in the metrics.
* Add timing metrics for the HTTP requests and the parsing operations.

## 0.1.1

Package metadata and documentation changes only, no code changes.

## 0.1.0

First public release.
