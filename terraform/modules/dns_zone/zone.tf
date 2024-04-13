variable "domain" {
  type=string
}

resource "google_dns_managed_zone" "default" {
  name        = join("", [replace(var.domain, ".", "-dot-"), "-zone"])
  dns_name    = "${var.domain}." # the trailing dot is important
  dnssec_config {
    state = "on"
  }
}

output "zone" {
  value = google_dns_managed_zone.default
}