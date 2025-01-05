module "cloudsql_user_role" {
  source      = "../../modules/custom_role"
  role_id     = "eave.cloudsqlUser"
  title       = "CloudSQL User for Apps"
  description = "Permissions needed to connect to and use CloudSQL"
  base_roles = [
    "roles/cloudsql.instanceUser", # for IAM auth
    "roles/cloudsql.client",
  ]
}

resource "google_project_iam_binding" "project_cloudsql_user_role_members" {
  lifecycle {
    prevent_destroy = true
  }

  project = data.google_project.default.project_id
  role    = module.cloudsql_user_role.id
  members = var.cloudsql_user_role_members

  condition {
    title       = "CloudSQL Instance Name"
    description = "Access limited to the given CloudSQL instance name"
    expression  = "resource.service == \"sqladmin.googleapis.com\" && resource.type == \"sqladmin.googleapis.com/Instance\" && resource.name == \"projects/${google_sql_database_instance.default.project}/instances/${google_sql_database_instance.default.id}\""
  }
}
