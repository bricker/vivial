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
    GAE_RELEASE_DATE = var.release_date
    LOG_LEVEL        = var.LOG_LEVEL
    COLLECTOR_ASSET_BASE = var.cdn_base_url
    EAVE_CLIENT_ID = var.EAVE_CREDENTIALS.CLIENT_ID
  }
}