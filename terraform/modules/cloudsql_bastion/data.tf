data "google_service_account" "app_service_account" {
  account_id = var.app_service_account_id
}

data "google_sql_database_instance" "given" {
  name = var.cloudsql_instance_name
}

data "google_compute_network" "given" {
  name = var.network_name
}

data "google_iam_role" "compute_vm_accessor_role" {
  name = var.compute_vm_accessor_role_name
}