resource "google_project_iam_custom_role" "default" {
  role_id     = var.role_id
  title       = var.title
  description = var.description
  # https://cloud.google.com/knowledge/kb/permission-error-for-custom-role-000004670
  permissions = setsubtract(distinct(flatten(
    [for _, role in data.google_iam_role.base_roles : role.included_permissions]
  )), ["resourcemanager.projects.list"])
}

resource "google_project_iam_binding" "default" {
  project = data.google_project.default.project_id
  role    = google_project_iam_custom_role.default.id
  members = var.members
}
