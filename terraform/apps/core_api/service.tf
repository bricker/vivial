resource "kubernetes_service" "app" {
  metadata {
    name = local.app_name
    namespace = var.kube_namespace_name
    annotations = {
      "beta.cloud.google.com/backend-config" = jsonencode({"default": kubernetes_manifest.backend_config.manifest.metadata.name})
    }

    labels = {
      app = local.app_name
    }
  }

  spec {
    selector = {
      app = local.app_name
    }

    type = "NodePort"
    port {
      name = local.service_port.name
      port = local.service_port.number
      protocol = "TCP"
      target_port = local.app_port.name
    }
  }
}


# module "kubernetes_service" {
#   source = "../../modules/kube_service"
#   namespace = var.kube_namespace_name
#   service_name = local.app_name
#   service_port = local.service_port
#   app_port_name = local.app_port.name
# }

# module "healthcheck_policy" {
#   source = "../../modules/kube_health_check_policy"
#   namespace = var.kube_namespace_name
#   service_name = module.kubernetes_service.name
#   app_port = module.kubernetes_service.port.target_port
# }