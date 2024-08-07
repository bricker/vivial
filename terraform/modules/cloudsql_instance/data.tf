data "google_compute_network" "given" {
  name = var.network_name
}

data "google_compute_global_address" "given" {
  name = var.global_address_name
}