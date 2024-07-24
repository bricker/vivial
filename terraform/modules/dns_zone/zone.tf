resource "google_dns_managed_zone" "default" {
  name     = join("", [replace(var.root_domain, ".", "-dot-"), "-zone"])
  dns_name = "${var.root_domain}." # the trailing dot is important
  dnssec_config {
    state = "on"
  }

  visibility = var.visibility
}
