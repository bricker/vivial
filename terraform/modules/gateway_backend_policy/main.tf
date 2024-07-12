resource "kubernetes_manifest" "backend_policy" {
  manifest = {
    apiVersion = "networking.gke.io/v1"
    kind       = "GCPBackendPolicy"
    metadata = {
      name      = var.name
      namespace = var.namespace
      labels    = var.labels
    }

    spec = {
      default = {
        # https://cloud.google.com/kubernetes-engine/docs/how-to/configure-gateway-resources#configure_iap
        iap = {
          enabled = true
          oauth2ClientSecret = {
            name = var.iap_oauth_client_secret_name
          }
          clientID = var.iap_oauth_client_id
        }
      }

      targetRef = {
        group = ""
        kind  = "Service"
        name  = var.service_name
      }
    }
  }
}
