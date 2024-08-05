module "custom_developer_role" {
  source  = "../../modules/custom_role"
  role_id = "eave.developers"
  title   = "Eave Developers"
  base_roles = [
    "roles/cloudsql.client",
    "roles/cloudsql.instanceUser",
    "roles/artifactregistry.writer",
    "roles/iap.httpsResourceAccessor",
  ]
  members = [
    "group:developers@eave.fyi",
  ]
}

module "custom_everybody_role" {
  source  = "../../modules/custom_role"
  role_id = "eave.everybody"
  title   = "All Eave Employees"
  base_roles = [
    "roles/iap.httpsResourceAccessor",
  ]
  members = [
    "group:everybody@eave.fyi",
  ]
}
