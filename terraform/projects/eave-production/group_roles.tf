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
