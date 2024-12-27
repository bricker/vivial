module "service_accounts" {
  # Create the app service account and KSA binding
  source              = "../../modules/gke_app_service_account"
  kube_service_name   = module.kubernetes_service.name
  kube_namespace_name = var.kube_namespace_name
}

module "app_iam_role" {
  # Create a role for this app
  source      = "../../modules/custom_role"
  role_id     = "eave.dashboardApp"
  title       = "Eave Dashboard App"
  description = "Project permissions needed by the Dashboard App"
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
