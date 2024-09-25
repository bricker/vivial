resource "google_project_service" "org_policy_service" {
  service = "orgpolicy.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
}

# resource "google_org_policy_policy" "primary" {
#   name   = "organizations/${data.google_project.default.org_id}/constraints/storage.publicAccessPrevention"
#   parent = "organizations/${data.google_project.default.org_id}"

#   spec {
#     rules {
#       enforce = "TRUE"
#     }
#   }
# }

resource "google_org_policy_policy" "enable_osconfig" {
  name   = "organizations/${data.google_project.default.org_id}/policies/compute.requireOsConfig"
  parent = "organizations/${data.google_project.default.org_id}"

  spec {
    rules {
      enforce = "TRUE"
    }
  }
}
