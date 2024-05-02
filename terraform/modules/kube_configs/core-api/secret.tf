resource "kubernetes_secret" "default" {
  metadata {
    name = "${local.app_name}-secret"
    namespace = local.kube_namespace
  }

  type = "Opaque"
  data = {
    "METABASE_UI_BIGQUERY_ACCESSOR_GSA_KEY_JSON_B64": "${var.METABASE_UI_BIGQUERY_ACCESSOR_GSA_KEY_JSON_B64}"
  }
}