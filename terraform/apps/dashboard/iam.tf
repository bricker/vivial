module "service_accounts" {
  source              = "../../modules/gke_app_service_account"
  kube_service_name   = module.kubernetes_service.name
  kube_namespace_name = var.kube_namespace_name
}

# Create custom role
module "app_iam_role" {
  source      = "../../modules/custom_role"
  role_id     = "eave.dashboardApp"
  title       = "Eave Dashboard App"
  description = "Project permissions needed by the Dashboard App"
  base_roles = [
    "roles/logging.logWriter",
  ]
}

resource "google_project_iam_binding" "gke_gsa_app_role" {
  project = data.google_project.default.project_id
  role    = module.app_iam_role.id
  members = [ "serviceAccount:${data.google_service_account.gke_gsa.email}" ]
}
