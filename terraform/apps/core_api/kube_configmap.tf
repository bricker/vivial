resource "kubernetes_config_map" "app" {
  lifecycle {
    prevent_destroy = true
  }

  metadata {
    name      = local.app_name
    namespace = var.kube_namespace_name

    labels = {
      app = local.app_name
    }
  }

  data = {
    LOG_LEVEL                  = var.LOG_LEVEL
    SEGMENT_CORE_API_WRITE_KEY = var.SEGMENT_CORE_API_WRITE_KEY
    JWS_SIGNING_KEY_VERSION_PATH = var.JWS_SIGNING_KEY_VERSION_PATH
  }
}
