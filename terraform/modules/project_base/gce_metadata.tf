resource "google_compute_project_metadata_item" "enable_oslogin" {
  # Mandatory for SOC-2 compliance
  key   = "enable-oslogin"
  value = "TRUE"
}
