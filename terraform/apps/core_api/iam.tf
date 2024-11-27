module "service_accounts" {
  # Create the app service account and KSA binding
  source              = "../../modules/gke_app_service_account"
  kube_service_name   = local.app_name
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
  members = [data.google_service_account.app_service_account.member]
}

resource "google_service_account_iam_binding" "sa_impersonator_role_members" {
  # Add impersonators to the app service account
  service_account_id = data.google_service_account.app_service_account.id
  role               = data.google_iam_role.impersonator_role.id
  members = [
    data.google_service_account.cloudsql_bastion_service_account.member
  ]
}