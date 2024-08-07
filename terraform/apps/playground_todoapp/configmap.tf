resource "kubernetes_config_map" "app" {
  metadata {
    name      = local.app_name
    namespace = var.kube_namespace_name

    labels = {
      app = local.app_name
    }

  }

  data = {
    LOG_LEVEL            = var.LOG_LEVEL
    EAVE_CLIENT_ID       = var.EAVE_CREDENTIALS.CLIENT_ID
    COLLECTOR_ASSET_BASE = var.cdn_base_url
  }
}