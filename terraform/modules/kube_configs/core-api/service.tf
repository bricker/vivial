resource "kubernetes_service" "default" {
  metadata {
    name = local.app_name
    namespace = local.kube_namespace
    annotations = {
      "beta.cloud.google.com/backend-config" = "{\"default\": \"shared-bc\"}"
    }
  }

  spec {
    selector = {
      "app" = "${local.app_name}-app"
    }

    type = "NodePort"
    port {
      name = "http"
      protocol = "TCP"
      port = 80
      target_port = "app"
    }
  }
}