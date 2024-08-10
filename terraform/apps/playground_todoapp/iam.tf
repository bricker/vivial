module "service_accounts" {
  source              = "../../modules/gke_app_service_account"
  kube_service_name   = module.kubernetes_service.name
  kube_namespace_name = var.kube_namespace_name
}

# Create custom role
module "app_iam_role" {
  source      = "../../modules/custom_role"
  role_id     = "eave.playgroundTodoApp"
  title       = "Eave Playground Todo App"
  description = "Project permissions needed by the Playground Todo App"
  base_roles = [
    "roles/logging.logWriter",
  ]
}

    # "roles/cloudsql.instanceUser", # for IAM auth
    # "roles/cloudsql.client",

resource "google_project_iam_binding" "gke_gsa_app_role" {
  project = data.google_project.default.project_id
  role    = module.app_iam_role.id
  members = [ "serviceAccount:${data.google_service_account.gke_gsa.email}" ]
}

resource "google_service_account_iam_binding" "impersonators" {
  service_account_id = data.google_service_account.gke_gsa.id
  role               = data.google_iam_role.impersonator_role.id
  members             = var.impersonators
}
