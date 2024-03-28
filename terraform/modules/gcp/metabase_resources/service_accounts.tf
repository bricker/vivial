variable "metabase_instances" {
  type = list(string)
}

variable "project_id" { type = string }

locals {
  metabase_roles = [
    "roles/cloudsql.client",
    "roles/logging.logWriter",
    "roles/iam.workloadIdentityUser",
  ]
}

resource "google_service_account" "metabase_service_accounts" {
  for_each = var.metabase_instances

  account_id   = each.value
  disabled     = false
}

resource "google_project_iam_binding" "metabase_roles" {
  depends_on = [ google_service_account.metabase_service_accounts ]
  for_each = local.metabase_roles

  project = var.project_id
  role    = each.value
  members = [for sa in google_service_account.metabase_service_accounts : "serviceAccount:${sa.email}"]
}