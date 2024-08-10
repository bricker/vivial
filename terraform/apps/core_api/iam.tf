module "service_accounts" {
  source              = "../../modules/gke_app_service_account"
  kube_service_name   = module.kubernetes_service.name
  kube_namespace_name = var.kube_namespace_name
}

module "app_iam_role" {
  source      = "../../modules/custom_role"
  role_id     = "eave.coreApiApp"
  title       = "Core API App"
  description = "Project permissions needed by the Core API App"
  base_roles = [
    "roles/logging.logWriter",
    "roles/bigquery.dataOwner",
    "roles/dlp.user",
  ]
}

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

resource "google_project_iam_binding" "app_cloudsql_iam_binding" {
  project = data.google_project.default.project_id
  role    = module.app_cloudsql_iam_role.id
  members = [ "serviceAccount:${data.google_service_account.gke_gsa.email}" ]
  condition {
    title = "CloudSQL Instance Name"
    description = "Access limited to the given CloudSQL instance name"
    expression = "resource.name == ${data.google_sql_database_instance.given.name}"
  }
}