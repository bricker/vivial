module "service_accounts" {
  # Create the app service account and KSA binding
  source              = "../../modules/gke_app_service_account"
  kube_service_name   = module.kubernetes_service.name
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
    "roles/bigquery.dataOwner",
    "roles/dlp.user",
  ]
}

resource "google_project_iam_binding" "app_service_account_iam_role_binding" {
  # Add the new app role to the app service account
  project = data.google_project.default.project_id
  role    = module.app_iam_role.id
  members = [ "serviceAccount:${data.google_service_account.app_service_account.email}" ]
}

resource "google_service_account_iam_binding" "app_service_account_impersonators" {
  # Add impersonators to the app service account
  count = var.impersonator_role_id == null ? 0 : 1

  service_account_id = data.google_service_account.app_service_account.id
  role               = var.impersonator_role_id
  members             = var.impersonators
}

resource "google_project_iam_binding" "app_cloudsql_user_iam_binding" {
  # Add the cloudsql user role to the service account
  project = data.google_project.default.project_id
  role    = var.cloudsql_user_role_id
  members = [ "serviceAccount:${data.google_service_account.app_service_account.email}" ]
  condition {
    title = "CloudSQL Instance Name"
    description = "Access limited to the given CloudSQL instance name"
    expression = "resource.service == sqladmin.googleapis.com && resource.type == sqladmin.googleapis.com/Instance && resource.name == ${data.google_sql_database_instance.given.id}"
  }
}