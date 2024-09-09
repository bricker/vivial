data "google_project" "default" {}

data "google_sql_database_instance" "given" {
  name = var.cloudsql_instance_name
}

data "google_iam_role" "cloudsql_user_role" {
  name = var.cloudsql_user_role_name
}