variable "kube_service_name" {
  type = string
}

variable "kube_namespace_name" {
  type = string
}

variable "project" {
  type = object({
    id = string
  })
}

data "google_iam_role" "workload_identity_role" {
  name = "roles/iam.workloadIdentityUser"
}

resource "google_service_account" "app_service_account" {
  account_id   = "gsa-app-${var.kube_service_name}"
  display_name = var.kube_service_name
  description = "KSA/GSA binding for ${var.kube_service_name}"
}

output "gsa" {
  value = google_service_account.app_service_account
}

resource "kubernetes_service_account" "app_ksa" {
  metadata {
    name = "ksa-app-${var.kube_service_name}"
    namespace = var.kube_namespace_name
    annotations = {
      "iam.gke.io/gcp-service-account" = google_service_account.app_service_account.email
    }

    labels = {
      app = var.kube_service_name
    }
  }
}

output "ksa_name" {
  value = kubernetes_service_account.app_ksa.metadata[0].name
}

resource "google_service_account_iam_member" "app_service_account_ksa_binding" {
  service_account_id = google_service_account.app_service_account.id
  role               = data.google_iam_role.workload_identity_role.id
  member             = "serviceAccount:${var.project.id}.svc.id.goog[${var.kube_namespace_name}/${kubernetes_service_account.app_ksa.metadata[0].name}]"
}
