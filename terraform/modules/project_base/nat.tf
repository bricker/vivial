resource "google_compute_router" "cloud_nat_router" {
  lifecycle {
    prevent_destroy = true
  }

  name    = "cloud-nat-router"
  network = google_compute_network.primary.id
}

resource "google_compute_router_nat" "cloud_nat" {
  lifecycle {
    prevent_destroy = true
  }

  name                               = "cloud-nat"
  router                             = google_compute_router.cloud_nat_router.name
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}
