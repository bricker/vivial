data "google_project" "default" {}

data "google_compute_global_address" "given" {
  name = var.global_address_name
}