# https://cloud.google.com/kubernetes-engine/docs/how-to/configure-gateway-resources#configure_health_check
resource "kubernetes_manifest" "healthcheck_policy" {
  lifecycle {
    prevent_destroy = true
  }

  manifest = {
    apiVersion = "networking.gke.io/v1"
    kind       = "HealthCheckPolicy"
    metadata = {
      name      = kubernetes_service.default.metadata[0].name
      namespace = kubernetes_service.default.metadata[0].namespace
    }

    spec = {
      default = {
        checkIntervalSec   = 30
        timeoutSec         = 25
        healthyThreshold   = 1
        unhealthyThreshold = 2
        logConfig = {
          enabled = true
        }
        config = {
          type = "HTTP"
          httpHealthCheck = {
            port        = var.app_port.number
            requestPath = "/healthz"
            response    = "1"
          }
        }
      }

      targetRef = {
        group = "" # This is a required attribute, can be empty
        kind  = "Service"
        name  = kubernetes_service.default.metadata[0].name
      }
    }
  }
}
