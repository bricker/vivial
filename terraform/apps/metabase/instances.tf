module "service_accounts" {
  source              = "../../modules/gke_app_service_account"
  for_each            = var.metabase_instances
  project             = var.project
  kube_service_name   = kubernetes_service.instances[each.key].metadata[0].name
  kube_namespace_name = var.kube_namespace_name
}

resource "google_sql_database" "instances" {
  for_each = var.metabase_instances
  name     = "mb_${each.value.metabase_instance_id}"
  instance = var.cloudsql_instance_name
}

resource "google_sql_user" "instances" {
  for_each        = var.metabase_instances
  instance        = var.cloudsql_instance_name
  name            = trimsuffix(module.service_accounts[each.key].gsa.email, ".gserviceaccount.com")
  type            = "CLOUD_IAM_SERVICE_ACCOUNT"
  password        = null # only IAM supported
  deletion_policy = "ABANDON"
}

# resource "google_service_account" "metabase_ui_gsa" {
#   for_each = var.metabase_instances
#   account_id   = "mb-ui-${each.value.metabase_instance_id}"
#   display_name = "Metabase UI - instance ${each.value.metabase_instance_id}"
#   description = "BigQuery access for Metabase UI - instance ${each.value.metabase_instance_id}"
# }

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

# We create a separate certificate per instance so that we don't have to replace the single cert every time we add an instance.
module "certificates" {
  source   = "../../modules/certificate_manager"
  for_each = var.metabase_instances

  certificate_map = var.certificate_map_name
  cert_name       = "mb-${each.value.metabase_instance_id}"
  entry_name      = "mb-${each.value.metabase_instance_id}"
  hostname        = "${each.value.metabase_instance_id}.${local.domain}"
}