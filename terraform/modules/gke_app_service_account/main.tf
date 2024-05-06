# variable "role_id" {
#   type=string
# }

variable "app" {
  type = string
}

variable "kube_namespace" {
  type = string
}

variable "project_id" {
  type = string
}

# data "google_iam_role" "app_role" {
#   name = var.role_id
# }

data "google_iam_role" "workload_identity_role" {
  name = "roles/iam.workloadIdentityUser"
}

resource "google_service_account" "app_service_account" {
  account_id   = "gsa-app-${var.app}"
  display_name = var.app
  description = "KSA/GSA binding for ${var.app}"
}

# resource "google_project_iam_member" "app_service_accounts_role_bindings" {
#   project = var.project_id
#   role    = data.google_iam_role.app_role.id
#   member = "serviceAccount:${google_service_account.app_service_account.email}"
# }

resource "kubernetes_service_account" "app_ksa" {
  metadata {
    name = "ksa-app-${var.app}"
    namespace = var.kube_namespace
    annotations = {
      "iam.gke.io/gcp-service-account" = google_service_account.app_service_account.email
    }
  }
}

resource "google_service_account_iam_member" "app_service_account_ksa_binding" {
  service_account_id = google_service_account.app_service_account.id
  role               = data.google_iam_role.workload_identity_role.id
  member             = "serviceAccount:${var.project_id}.svc.id.goog[${var.kube_namespace}/${kubernetes_service_account.app_ksa.metadata.0.name}]"
}

output "gsa" {
  value = google_service_account.app_service_account
}

output "ksa" {
  value = kubernetes_service_account.app_ksa
}