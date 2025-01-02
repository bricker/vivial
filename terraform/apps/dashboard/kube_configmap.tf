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
    EAVE_DASHBOARD_IAP_JWT_AUD         = var.iap_jwt_aud
  }
}
