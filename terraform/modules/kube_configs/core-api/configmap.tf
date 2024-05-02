resource "kubernetes_config_map" "default" {
  metadata {
    name = "${local.app_name}-configmap"
    namespace = local.kube_namespace
  }

  data = {
    "EAVE_DB_NAME" = "eave"
    "GAE_SERVICE" = local.app_name
    "GAE_VERSION" = "${GAE_VERSION}"
    "GAE_RELEASE_DATE" = "${GAE_RELEASE_DATE}"
    "LOG_LEVEL" = "debug"
  }
}