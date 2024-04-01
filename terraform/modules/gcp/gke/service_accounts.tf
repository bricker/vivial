variable "google_service_accounts" {
  type = map(object({
    bound_ksa = string
  }))
}

variable "roles" {
  type = map(object({
    google_service_accounts = list(string)
  }))
}

resource "google_service_account" "service_accounts" {
  for_each = var.google_service_accounts
  account_id   = each.key
}

resource "google_project_iam_binding" "roles" {
  for_each = var.roles

  project = var.project_id
  role    = each.key
  members = [for sa in each.value.google_service_accounts : "serviceAccount:${google_service_account.service_accounts[sa].email}"]
}

resource "google_service_account_iam_binding" "gsa_ksa_binding" {
  for_each = var.google_service_accounts

  service_account_id = google_service_account.service_accounts[each.key].id
  role               = "roles/iam.workloadIdentityUser"

  members = [
    "serviceAccount:${var.project_id}.svc.id.goog[${each.value.bound_ksa}]"
  ]
}
