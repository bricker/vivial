data "google_project" "default" {}

data "google_certificate_manager_certificate_map" "given" {
  name = var.certificate_map_name
}
