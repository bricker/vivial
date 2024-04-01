# For more examples: https://github.com/terraform-google-modules/terraform-google-cloud-nat

resource "google_compute_router" "router" {
  depends_on = [ google_compute_network.default ]
  project = var.project_id
  name    = "cloud-nat-router"
  network = google_compute_network.default.name
  region  = var.region
}

resource "google_compute_router_nat" "nat" {
  depends_on = [ google_compute_router.router ]
  project                             = var.project_id
  region                              = var.region
  name                                = "cloud-nat"
  router                              = google_compute_router.router.name
  nat_ip_allocate_option              = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat  = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}
