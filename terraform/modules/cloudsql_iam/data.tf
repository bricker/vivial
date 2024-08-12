data "google_project" "default" {}

data "google_sql_database_instance" "given" {
  name = var.cloudsql_instance_name
}