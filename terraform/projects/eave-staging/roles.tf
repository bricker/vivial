data "google_iam_role" "cloud_sql_client" {
  name = "roles/cloudsql.client"
}

resource "google_project_iam_custom_role" "eave_developers_role" {
  role_id     = "eave.developers"
  title       = "Eave Developers"
  permissions = concat(
    data.google_iam_role.cloud_sql_client.included_permissions
  )
}

resource "google_project_iam_binding" "eave_developers_binding" {
  project = local.project_id
  role = google_project_iam_custom_role.eave_developers_role.id
  members = [
    "group:eave-developers@eave.fyi",
  ]
}
