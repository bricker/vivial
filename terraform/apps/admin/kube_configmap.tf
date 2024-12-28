resource "kubernetes_config_map" "app" {
  lifecycle {
    prevent_destroy = true
  }

  metadata {
    name      = local.app_name
    namespace = var.kube_namespace_name
  }

  data = {
    LOG_LEVEL = var.LOG_LEVEL
    EAVE_ADMIN_IAP_JWT_AUD = "/projects/${data.google_project.default.number}/global/backendServices/${data.google_compute_backend_service.admin_gw.id}"
  }
}
