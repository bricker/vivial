resource "kubernetes_config_map" "app" {
  metadata {
    name      = local.app_name
    namespace = var.kube_namespace_name

    labels = {
      app = local.app_name
    }

  }

  data = {
    GAE_SERVICE      = local.app_name
    GAE_VERSION      = var.release_version
    LOG_LEVEL        = var.LOG_LEVEL
  }
}