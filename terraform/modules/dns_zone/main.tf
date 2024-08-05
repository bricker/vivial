resource "google_dns_managed_zone" "default" {
  name     = join("", [replace(var.root_domain, ".", "-dot-"), "-zone"])
  dns_name = "${var.root_domain}." # the trailing dot is important
  dnssec_config {
    state = "on"
  }

  visibility = var.visibility
}

resource "google_dns_record_set" "records" {
  count = length(var.records)

  managed_zone = google_dns_managed_zone.default.name
  name         = join(".", compact([var.records[count.index].subdomain, google_dns_managed_zone.default.dns_name]))
  type         = var.records[count.index].type
  ttl          = 300
  rrdatas      = var.records[count.index].datas
}
