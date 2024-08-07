data "google_project" "default" {}

data "google_compute_network" "given" {
  name = var.network_name
}
