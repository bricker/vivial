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
    LOG_LEVEL                 = var.LOG_LEVEL
    SEGMENT_WEBSITE_WRITE_KEY = var.SEGMENT_WEBSITE_WRITE_KEY
    STRIPE_PUBLISHABLE_KEY    = var.STRIPE_PUBLISHABLE_KEY
  }
}
