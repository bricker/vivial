module "admin_dashboard_accessor_role" {
  source  = "../../modules/custom_role"
  role_id = "eave.adminDashboardAccessor"
  title   = "Eave Admin Dashboard Accessors"
  base_roles = [
    "roles/iap.httpsResourceAccessor",
  ]
}

resource "google_project_iam_binding" "project_admin_dashboard_accessor_role_members" {
  project = data.google_project.default.id
  role    = module.admin_dashboard_accessor_role.id
  members = [
    "group:everybody@eave.fyi",
  ]
}
