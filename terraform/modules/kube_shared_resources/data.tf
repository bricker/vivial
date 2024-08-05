data "google_project" "default" {}

data "google_iap_client" "given" {
  brand = var.iap_client_ref.brand
  client_id = var.iap_client_ref.client_id
}