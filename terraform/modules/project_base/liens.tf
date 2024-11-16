resource "google_resource_manager_lien" "main" {
  lifecycle {
    prevent_destroy = true
  }

  parent       = "projects/${data.google_project.default.number}"
  restrictions = ["resourcemanager.projects.delete"]
  reason       = "Terraform-managed GCP Projects should never be deleted."
  origin       = "terraform-project-deletion-prevention"
}
