resource "google_compute_router" "cloud_nat_router" {
  name    = "cloud-nat-router"
  network = google_compute_network.default.id
}

resource "google_compute_router_nat" "cloud_nat" {
  name                               = "cloud-nat"
  router                             = google_compute_router.cloud_nat_router.name
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}



# resource "google_compute_router" "primary_nat_router" {
#   name    = "primary-nat-router"
#   network = google_compute_network.primary.id
# }

# resource "google_compute_router_nat" "primary_nat" {
#   name                               = "primary-nat"
#   router                             = google_compute_router.primary_nat_router.name
#   nat_ip_allocate_option             = "AUTO_ONLY"
#   source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
# }
