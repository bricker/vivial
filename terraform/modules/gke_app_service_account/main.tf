resource "google_service_account" "app_service_account" {
  lifecycle {
    prevent_destroy = true
  }

  account_id   = substr("gsa-app-${var.kubernetes_service.name}", 0, 26)
  display_name = var.kubernetes_service.name
  description  = "${var.kubernetes_service.name} app service account"
}

resource "kubernetes_service_account" "app_ksa" {
  lifecycle {
    prevent_destroy = true
  }

  metadata {
    name      = substr("ksa-app-${var.kubernetes_service.name}", 0, 26)
    namespace = var.kube_namespace_name
    annotations = {
      "iam.gke.io/gcp-service-account" = google_service_account.app_service_account.email
    }
  }
}

resource "google_service_account_iam_binding" "app_service_account_ksa_binding" {
  lifecycle {
    prevent_destroy = true
  }

  service_account_id = google_service_account.app_service_account.id
  role               = data.google_iam_role.workload_identity_role.id
  members = [
    "serviceAccount:${data.google_project.default.project_id}.svc.id.goog[${var.kube_namespace_name}/${kubernetes_service_account.app_ksa.metadata[0].name}]"
  ]
}
