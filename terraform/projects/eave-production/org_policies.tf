resource "google_project_service" "orgpolicy" {
  service = "orgpolicy.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
}

resource "google_org_policy_policy" "primary" {
  name   = "organizations/${module.project_base.gcp_project.org_id}/constraints/storage.publicAccessPrevention"
  parent = "organizations/${module.project_base.gcp_project.org_id}"

  spec {
    rules {
      enforce = "TRUE"
    }
  }
}