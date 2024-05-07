module "service_accounts" {
  source         = "../../../modules/gke_app_service_account"
  project     = var.project
  kube_service_name            = local.app_name
  kube_namespace_name = var.kube_namespace_name
}

output "service_accounts" {
  value = module.service_accounts
}

resource "google_sql_database" "app" {
  name     = "mb_${var.metabase_instance_id}"
  instance = var.cloudsql_instance_name
}

resource "google_sql_user" "app" {
  instance        = var.cloudsql_instance_name
  name            = trimsuffix(module.service_accounts.gsa.email, ".gserviceaccount.com")
  type            = "CLOUD_IAM_SERVICE_ACCOUNT"
  password        = null # only IAM supported
  deletion_policy = "ABANDON"
}
