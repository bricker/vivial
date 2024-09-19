resource "google_dns_managed_zone" "default" {
  name     = join("", [replace(var.root_domain, ".", "-dot-"), "-zone"])
  dns_name = "${var.root_domain}." # the trailing dot is important
  dnssec_config {
    state = "on"
  }

  visibility = var.visibility
}

resource "google_dns_record_set" "records" {
  for_each = {
    for record in var.records : join("_", [record.type, coalesce(record.subdomain, "apex")]) => record
  }

  managed_zone = google_dns_managed_zone.default.name
  name         = join(".", compact([each.value.subdomain, google_dns_managed_zone.default.dns_name]))
  type         = each.value.type
  ttl          = 300
  rrdatas      = each.value.datas
}
