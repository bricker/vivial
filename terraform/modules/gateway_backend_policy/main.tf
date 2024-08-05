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
        iap = var.iap_enabled ? {
          enabled = var.iap_enabled
          oauth2ClientSecret = {
            name = var.iap_client_kube_secret_name
          }
          clientID = try(var.iap_client_ref.client_id, null)
        } : null
      }

      targetRef = {
        group = ""
        kind  = "Service"
        name  = var.service_name
      }
    }
  }
}
