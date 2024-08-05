locals {
  # eave.fyi. -> eave.fyi
  root_domain = trimsuffix(var.zone.dns_name, ".")
}