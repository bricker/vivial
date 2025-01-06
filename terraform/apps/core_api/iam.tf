module "service_accounts" {
  # Create the app service account and KSA binding
  source              = "../../modules/gke_app_service_account"
  app_name   = local.app_name
  kube_namespace_name = var.kube_namespace_name
}

module "app_iam_role" {
  # Create a role for this app
  source      = "../../modules/custom_role"
  role_id     = "eave.coreApiApp"
  title       = "Core API App"
  description = "Project permissions needed by the Core API App"
  base_roles = [
    "roles/logging.logWriter",
  ]
}

resource "google_project_iam_binding" "project_app_role_members" {
  lifecycle {
    prevent_destroy = true
  }

  # Add the new app role to the app service account
  project = data.google_project.default.project_id
  role    = module.app_iam_role.id
  members = [module.service_accounts.google_service_account.member]
}

resource "google_service_account_iam_binding" "sa_impersonator_role_members" {
  # Add impersonators to the app service account
  service_account_id = module.service_accounts.google_service_account.id
  role               = data.google_iam_role.impersonator_role.id
  members = [
    data.google_service_account.cloudsql_bastion_service_account.member
  ]
}

resource "google_kms_crypto_key_iam_member" "jws_signing_key_viewer_iam_binding" {
  crypto_key_id = var.google_kms_crypto_key_jws_signing_key.id
  role          = "roles/cloudkms.viewer"
  member        = module.service_accounts.google_service_account.member
}

resource "google_kms_crypto_key_iam_member" "jws_signing_key_signer_verifier_iam_binding" {
  crypto_key_id = var.google_kms_crypto_key_jws_signing_key.id
  role          = "roles/cloudkms.signerVerifier"
  member        = module.service_accounts.google_service_account.member
}
