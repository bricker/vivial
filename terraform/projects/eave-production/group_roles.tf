module "custom_everybody_role" {
  source  = "../../modules/custom_role"
  role_id = "eave.everybody"
  title   = "All Eave Employees"
  base_roles = [
    "roles/iap.httpsResourceAccessor",
  ]
}

resource "google_project_iam_binding" "project_everybody_role_members" {
  project = data.google_project.default.id
  role    = module.custom_everybody_role.id
  members = [
    "group:everybody@eave.fyi",
  ]
}
