resource "google_certificate_manager_certificate_map" "default" {
  lifecycle {
    prevent_destroy = true
  }

  name = "root-certificate-map"
}
