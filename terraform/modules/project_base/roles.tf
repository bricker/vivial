module "impersonator_role" {
  source      = "../../modules/custom_role"
  role_id     = "eave.impersonator"
  title       = "Service Account Impersonator"
  description = "Permissions needed to impersonate a service account"
  base_roles = [
    "roles/iam.serviceAccountTokenCreator",
  ]
}