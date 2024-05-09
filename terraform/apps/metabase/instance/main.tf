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

resource "google_service_account" "metabase_ui_gsa" {
  account_id   = "mb-ui-${var.metabase_instance_id}"
  display_name = "Metabase UI - instance ${var.metabase_instance_id}"
  description = "BigQuery access for Metabase UI - instance ${var.metabase_instance_id}"
}

# resource "google_bigquery_dataset_iam_binding" "dataset_iam_binding" {
#   dataset_id = "team_${var.metabase_instance_id}"
#   role       = "roles/bigquery.jobUser"

#   members = [
#     "serviceAccount:${google_service_account.metabase_ui_gsa.email}"
#   ]
# }

# resource "google_bigquery_dataset_iam_member" "dataset_iam_member" {
#   dataset_id = "team_${var.metabase_instance_id}"
#   role       = "roles/bigquery.jobUser"
#   member     = "serviceAccount:${google_service_account.metabase_ui_gsa.email}"
# }
