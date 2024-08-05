resource "google_iap_client" "default" {
  brand        = "projects/${data.google_project.default.number}/brands/${data.google_project.default.number}"
  display_name = "Default IAP"
}
