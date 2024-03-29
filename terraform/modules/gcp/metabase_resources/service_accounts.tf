variable "metabase_instances" {
  type = set(string)
}

variable "project_id" { type = string }

locals {
  metabase_roles = toset([
    "roles/cloudsql.client",
    "roles/logging.logWriter",
  ])
}

resource "google_service_account" "metabase_service_accounts" {
  for_each = var.metabase_instances
  account_id   = each.value
}

resource "google_project_iam_binding" "metabase_roles" {
  depends_on = [ google_service_account.metabase_service_accounts ]
  for_each = local.metabase_roles

  project = var.project_id
  role    = each.value
  members = [for sa in google_service_account.metabase_service_accounts : "serviceAccount:${sa.email}"]
}

resource "google_service_account_iam_binding" "gsa_ksa_binding" {
  depends_on = [ google_service_account.metabase_service_accounts ]
  for_each = var.metabase_instances

  service_account_id = google_service_account.metabase_service_accounts[each.key].id
  role               = "roles/iam.workloadIdentityUser"

  members = [
    "serviceAccount:${var.project_id}.svc.id.goog[metabase/ksa-${each.value}]"
  ]
}
