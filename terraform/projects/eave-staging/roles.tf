locals {
  developers_group_email = "developers@eave.fyi"
}

data "google_iam_role" "cloudsql_client" {
  name = "roles/cloudsql.client"
}

data "google_iam_role" "cloudsql_instanceuser" {
  name = "roles/cloudsql.instanceUser"
}

data "google_iam_role" "artifactregistry_writer" {
  name = "roles/artifactregistry.writer"
}


resource "google_project_iam_custom_role" "eave_developers_role" {
  role_id     = "eave.developers"
  title       = "Eave Developers"
  permissions = concat(
    data.google_iam_role.cloudsql_client.included_permissions,
    data.google_iam_role.cloudsql_instanceuser.included_permissions,
    data.google_iam_role.artifactregistry_writer.included_permissions,
  )
}

resource "google_project_iam_binding" "eave_developers_binding" {
  project = local.project_id
  role = google_project_iam_custom_role.eave_developers_role.id
  members = [
    "group:${local.developers_group_email}",
  ]
}
