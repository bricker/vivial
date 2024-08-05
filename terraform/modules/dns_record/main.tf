resource "google_dns_record_set" "default" {
  managed_zone = data.google_dns_managed_zone.given.name

  # if domain prefix given: "api.eave.fyi."
  # if domain prefix is empty string: "eave.fyi."
  name = join(".", compact([var.domain_prefix, data.google_dns_managed_zone.given.dns_name]))

  type = var.record_type
  ttl  = 300

  rrdatas = [data.google_compute_global_address.given.name]
}
