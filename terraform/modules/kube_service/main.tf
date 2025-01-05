resource "kubernetes_service" "default" {
  lifecycle {
    prevent_destroy = true
  }

  metadata {
    name      = var.service_name
    namespace = var.namespace
  }

  spec {
    selector = {
      app = var.app_name
    }

    type = "NodePort"
    port {
      protocol    = "TCP"
      name        = var.service_port.name
      port        = var.service_port.number
      target_port = var.app_port.name
    }
  }
}
