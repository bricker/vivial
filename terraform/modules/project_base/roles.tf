module "impersonator_role" {
  source      = "../../modules/custom_role"
  role_id     = "eave.impersonator"
  title       = "Service Account Impersonator"
  description = "Permissions needed to impersonate a service account"
  base_roles = [
    "roles/iam.serviceAccountTokenCreator",
  ]
}

module "secret_accessor_role" {
  source      = "../../modules/custom_role"
  role_id     = "eave.secretAccessor"
  title       = "Secret Manager Secret Accessor"
  description = "Permissions needed to access secret manager secrets"
  base_roles = [
    "roles/secretmanager.secretAccessor"
  ]
}

module "cloudsql_user_role" {
  source      = "../../modules/custom_role"
  role_id     = "eave.cloudsqlUser"
  title       = "CloudSQL User for Apps"
  description = "Permissions needed to connect to and use CloudSQL"
  base_roles = [
    "roles/cloudsql.instanceUser", # for IAM auth
    "roles/cloudsql.client",
  ]
}