resource "kubernetes_manifest" "backend_policy" {
  # https://googlecloudplatform.github.io/gke-gateway-api/#gcpbackendpolicy

  lifecycle {
    prevent_destroy = true
  }

  manifest = {
    apiVersion = "networking.gke.io/v1"
    kind       = "GCPBackendPolicy"
    metadata = {
      name      = kubernetes_service.default.metadata[0].name
      namespace = kubernetes_service.default.metadata[0].namespace
    }

    spec = {
      default = {
        # https://cloud.google.com/kubernetes-engine/docs/how-to/configure-gateway-resources#configure_iap
        iap = {
          enabled = var.iap_enabled
        }

        logging = {
          enabled    = true
          sampleRate = 1000000 # 100% sample rate
        }
      }

      targetRef = {
        group = ""
        kind  = "Service"
        name  = kubernetes_service.default.metadata[0].name
      }
    }
  }
}
