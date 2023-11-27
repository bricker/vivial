variable "project_id" {
  type = string
}

resource "google_project_iam_binding" "cloud_sql_client" {
  depends_on = [google_service_account.app_service_accounts]

  project = var.project_id
  role    = "roles/cloudsql.client"

  members = [
    "serviceAccount:${var.project_id}@appspot.gserviceaccount.com", // appengine
    "serviceAccount:${google_service_account.app_service_accounts["eave_core"].email}",
  ]
}

resource "google_project_iam_binding" "apps" {
  depends_on = [
    google_service_account.app_service_accounts,
    google_project_iam_custom_role.eave_apps
  ]

  project = var.project_id
  role    = google_project_iam_custom_role.eave_apps.id
  members = [for sa in google_service_account.app_service_accounts : "serviceAccount:${sa.email}"]
}


resource "google_service_account_iam_binding" "gsa_ksa_bindings" {
  depends_on = [
    google_service_account.app_service_accounts,
  ]

  for_each = google_service_account.app_service_accounts

  service_account_id = each.value.id
  role               = "roles/iam.workloadIdentityUser"

  members = [
    "serviceAccount:${var.project_id}.svc.id.goog[default/${each.value.account_id}]"
  ]
}
