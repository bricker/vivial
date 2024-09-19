resource "google_project" "main" {
  lifecycle {
    prevent_destroy = true
  }
  billing_account     = var.billing_account
  org_id              = var.org_id
  project_id          = var.project_id
  name                = var.project_id
  auto_create_network = false
}

resource "google_resource_manager_lien" "main" {
  lifecycle {
    prevent_destroy = true
  }

  parent       = "projects/${google_project.main.number}"
  restrictions = ["resourcemanager.projects.delete"]
  reason       = "Terraform-managed GCP Projects should never be deleted."
  origin       = "terraform-project-deletion-prevention"
}
