resource "google_project" "main" {
  billing_account     = var.billing_account
  org_id              = var.org_id
  project_id          = var.project_id
  name                = var.project_id
  auto_create_network = false
  skip_delete         = true
}
