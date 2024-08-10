module "impersonator_role" {
  source      = "../../modules/custom_role"
  role_id     = "eave.impersonator"
  title       = "Service Account Impersonator"
  description = "Permissions needed to impersonate a service account"
  base_roles = [
    "roles/iam.serviceAccountTokenCreator",
  ]
}

module "cloudsql_user_role" {
  source      = "../../modules/custom_role"
  role_id     = "eave.cloudsqlUser"
  title       = "CloudSQL User for Apps"
  description = "Permissions needed by the apps to connect to CloudSQL"
  base_roles = [
    "roles/cloudsql.instanceUser", # for IAM auth
    "roles/cloudsql.client",
  ]
}
