output "name" {
  value = kubernetes_service.default.metadata[0].name
}

output "port" {
  value = {
    name   = kubernetes_service.default.spec[0].port[0].name
    number = kubernetes_service.default.spec[0].port[0].port
  }
}

output "target_port_name" {
  value = kubernetes_service.default.spec[0].port[0].target_port
}