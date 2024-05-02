resource "kubernetes_service_account" "default" {
  metadata {
    name = "ksa-app-${local.app_name}"
    namespace = local.kube_namespace
    annotations = {
      "iam.gke.io/gcp-service-account" = "gsa-app-${local.app_name}@${var.project_id}.iam.gserviceaccount.com"
    }
  }
}