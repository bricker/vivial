# For more examples: https://github.com/terraform-google-modules/terraform-google-cloud-nat

variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "network_id" {
  type = string
}

resource "google_compute_router" "cloud_nat_router" {
  name    = "cloud-nat-router"
  network = var.network_id
  project = var.project_id
  region = var.region
}

resource "google_compute_router_nat" "cloud_nat" {
  name                                = "cloud-nat"
  router                              = google_compute_router.main.name
  nat_ip_allocate_option              = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat  = "ALL_SUBNETWORKS_ALL_IP_RANGES"
  project = var.project_id
  region = var.region
}
