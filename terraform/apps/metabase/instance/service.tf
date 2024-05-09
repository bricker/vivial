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

output "kubernetes_service" {
  value = kubernetes_service.app
}

resource "kubernetes_manifest" "backend_config" {
  # Standard app healthcheck/backend config
  # Assumes the app is listening on port 8000 and has a /status endpoint.
  # Also:
  # - Removes any "server" response header, for security.
  # - Adds a special header to indicate to the backend that the request flowed through this ingress.

  manifest = {
    apiVersion = "cloud.google.com/v1"
    kind       = "BackendConfig"
    metadata = {
      name = local.app_name
      namespace = var.kube_namespace_name

      labels = {
        app = local.app_name
      }
    }

    spec = {
      iap = {
        enabled = true
        oauthclientCredentials = {
          secretName = var.iap_oauth_client_credentials_secret_name
        }
      }

      healthCheck = {
        type = "HTTP"
        requestPath = "/api/health"
        port = local.app_port.number
        checkIntervalSec = 30
        unhealthyThreshold = 4
      }

      logging = {
        enable = true
        sampleRate = 0.5
      }

      customRequestHeaders = {
        headers = [
          "eave-lb: 1"
        ]
      }

      customResponseHeaders = {
        headers = [
          "server: n/a"
        ]
      }
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
#           type = "TCP"
#           httpHealthCheck = {
#             portName = kubernetes_service.app.spec[0].port[0].target_port
#             requestPath = "/api/health"
#             response = jsonencode({"status":"ok"})
#           }
#         }
#       }

#       targetRef = {
#         group = ""
#         kind = "Service"
#         name = kubernetes_service.app.metadata[0].name
#       }
#     }
#   }
# }