resource "kubernetes_config_map" "app" {
  lifecycle {
    prevent_destroy = true
  }

  metadata {
    name      = local.app_name
    namespace = var.kube_namespace_name
  }

  data = {
    LOG_LEVEL                     = var.LOG_LEVEL
    JWS_SIGNING_KEY_VERSION_PATH  = var.JWS_SIGNING_KEY_VERSION_PATH
    EAVE_API_IAP_JWT_AUD = var.internal_iap_jwt_aud # DEPRECATED - needed for backwards compat until next core deployment
    EAVE_API_INTERNAL_IAP_JWT_AUD = var.internal_iap_jwt_aud
    EAVE_API_ROOT_IAP_ENABLED     = var.root_iap_enabled ? "1" : null
    EAVE_API_ROOT_IAP_JWT_AUD     = var.root_iap_jwt_aud
  }
}
