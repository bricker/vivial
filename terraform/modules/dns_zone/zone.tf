variable "project" {
  type = object({
    root_domain = string
  })
}

variable "visibility" {
  type = string
  default = "public"
}

resource "google_dns_managed_zone" "default" {
  name     = join("", [replace(var.project.root_domain, ".", "-dot-"), "-zone"])
  dns_name = "${var.project.root_domain}." # the trailing dot is important
  dnssec_config {
    state = "on"
  }

  visibility = var.visibility
}

output "zone" {
  value = google_dns_managed_zone.default
}