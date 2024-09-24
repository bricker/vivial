# resource "google_org_policy_policy" "primary" {
#   name   = "organizations/${module.project_base.gcp_project.org_id}/constraints/storage.publicAccessPrevention"
#   parent = "organizations/${module.project_base.gcp_project.org_id}"

#   spec {
#     rules {
#       enforce = "TRUE"
#     }
#   }
# }

resource "google_org_policy_policy" "enable_osconfig" {
  name   = "organizations/${module.project_base.gcp_project.org_id}/constraints/compute.requireOsConfig"
  parent = "organizations/${module.project_base.gcp_project.org_id}"

  spec {
    rules {
      enforce = "TRUE"
    }
  }
}