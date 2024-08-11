resource "google_service_account" "app_service_account" {
  account_id   = substr("gsa-app-${var.kube_service_name}", 0, 26)
  display_name = var.kube_service_name
  description  = "${var.kube_service_name} app service account"
}

resource "kubernetes_service_account" "app_ksa" {
  metadata {
    name      = substr("ksa-app-${var.kube_service_name}", 0, 26)
    namespace = var.kube_namespace_name
    annotations = {
      "iam.gke.io/gcp-service-account" = google_service_account.app_service_account.email
    }

    labels = {
      app = var.kube_service_name
    }
  }
}

resource "google_service_account_iam_binding" "app_service_account_ksa_binding" {
  service_account_id = google_service_account.app_service_account.id
  role               = data.google_iam_role.workload_identity_role.id
  members             = [
    "serviceAccount:${data.google_project.default.project_id}.svc.id.goog[${var.kube_namespace_name}/${kubernetes_service_account.app_ksa.metadata[0].name}]"
  ]
}
