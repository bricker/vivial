variable "apps" {
  type = map(object({
    id = string
    ksa = string
  }))
}

variable "roles" {
  type = map(object({
    role = string
    apps = list(string)
  }))
}

variable "project_id" { type = string }

resource "google_service_account" "app_service_accounts" {
  for_each = var.apps
  account_id   = each.value["id"]
}

resource "google_project_iam_binding" "app_roles" {
  depends_on = [ google_service_account.app_service_accounts ]
  for_each = var.roles

  project = var.project_id
  role    = each.value["role"]
  members = [for app in each.value["apps"] : "serviceAccount:${google_service_account.app_service_accounts[app].email}"]
}

resource "google_service_account_iam_binding" "gsa_ksa_binding" {
  depends_on = [ google_service_account.app_service_accounts ]
  for_each = var.apps

  service_account_id = google_service_account.app_service_accounts[each.value["id"]].id
  role               = "roles/iam.workloadIdentityUser"

  members = [
    "serviceAccount:${var.project_id}.svc.id.goog[${each.value["ksa"]}]"
  ]
}
