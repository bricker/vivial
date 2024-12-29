# https://cloud.google.com/kubernetes-engine/docs/concepts/gateway-api
resource "kubernetes_manifest" "gateway" {
  lifecycle {
    prevent_destroy = true
  }

  field_manager {
    force_conflicts = true
  }

  manifest = {
    apiVersion = "gateway.networking.k8s.io/v1beta1"
    kind       = "Gateway"
    metadata = {
      name      = var.service_name
      namespace = var.namespace

      annotations = {
        "networking.gke.io/certmap" : var.google_certificate_manager_certificate_map.name
      }
    }

    spec = {
      # https://cloud.google.com/kubernetes-engine/docs/concepts/gateway-api#gatewayclass
      gatewayClassName = "gke-l7-global-external-managed"
      listeners = [
        {
          name     = "https"
          protocol = "HTTPS"
          port     = 443

          # This block is NOT needed because TLS is configured by certificate manager
          # tls = {
          #   mode = "Terminate"
          #   options = {
          #     "networking.gke.io/pre-shared-certs" = kubernetes_manifest.managed_certificate.manifest.metadata.name
          #   }
          # }

          allowedRoutes = {
            kinds = [
              {
                kind = "HTTPRoute"
              }
            ]
          }
        }
      ]

      addresses = [
        for addr in data.google_compute_global_address.given :
        {
          type  = "NamedAddress"
          value = addr.name
        }
      ]
    }
  }
}

# https://cloud.google.com/kubernetes-engine/docs/how-to/configure-gateway-resources#configure_ssl_policies
resource "kubernetes_manifest" "gateway_policy" {
  lifecycle {
    prevent_destroy = true
  }

  manifest = {
    apiVersion = "networking.gke.io/v1"
    kind       = "GCPGatewayPolicy"
    metadata = {
      name      = var.service_name
      namespace = var.namespace
    }

    spec = {
      default = {
        sslPolicy = var.google_compute_ssl_policy.name
      }

      targetRef = {
        group = "gateway.networking.k8s.io"
        kind  = "Gateway"
        name  = kubernetes_manifest.gateway.manifest.metadata.name
      }
    }
  }
}
