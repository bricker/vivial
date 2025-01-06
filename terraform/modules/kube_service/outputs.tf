output "kubernetes_service" {
  value = {
    name = kubernetes_service.default.metadata[0].name
    port = {
      name        = kubernetes_service.default.spec[0].port[0].name
      number      = kubernetes_service.default.spec[0].port[0].port
      target_port = kubernetes_service.default.spec[0].port[0].target_port
    }
  }
}
