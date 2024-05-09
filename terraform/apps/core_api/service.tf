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


# # https://cloud.google.com/kubernetes-engine/docs/how-to/configure-gateway-resources#configure_health_check
# resource "kubernetes_manifest" "healthcheck_policy" {
#   manifest = {
#     apiVersion = "networking.gke.io/v1"
#     kind       = "HealthCheckPolicy"
#     metadata = {
#       name = local.app_name
#       namespace = var.kube_namespace_name

#       labels = {
#         app = local.app_name
#       }
#     }

#     spec = {
#       default = {
#         checkIntervalSec = 30
#         timeoutSec = 25
#         healthyThreshold = 1
#         unhealthyThreshold = 2
#         logConfig = {
#           enabled = true
#         }
#         config = {
#           type = "HTTP"
#           httpHealthCheck = {
#             portName = local.app_port.name
#             requestPath = "/healthz"
#             response = "1"
#           }
#         }
#       }

#       targetRef = {
#         kind = "Service"
#         name = kubernetes_service.app.metadata[0].name
#       }
#     }
#   }
# }