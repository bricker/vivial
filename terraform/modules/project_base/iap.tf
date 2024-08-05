resource "google_iap_client" "default" {
  brand        = "projects/${data.google_project.default.org_id}/brands/${data.google_project.default.org_id}"
  display_name = "Default IAP"
}
