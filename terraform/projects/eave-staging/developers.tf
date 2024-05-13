module "custom_developer_role" {
  source  = "../../modules/custom_role"
  project = local.project
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
