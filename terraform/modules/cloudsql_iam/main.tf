resource "google_project_iam_binding" "project_cloudsql_user_role_members" {
  project = data.google_project.default.project_id
  role    = data.google_iam_role.cloudsql_user_role.id
  members = var.members
  condition {
    title = "CloudSQL Instance Name"
    description = "Access limited to the given CloudSQL instance name"
    expression = "resource.service == \"sqladmin.googleapis.com\" && resource.type == \"sqladmin.googleapis.com/Instance\" && resource.name == \"${data.google_sql_database_instance.given.id}\""
  }
}