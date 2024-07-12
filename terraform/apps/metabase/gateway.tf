# https://cloud.google.com/kubernetes-engine/docs/concepts/gateway-api
resource "kubernetes_manifest" "gateway" {
  manifest = {
    apiVersion = "gateway.networking.k8s.io/v1beta1"
    kind       = "Gateway"
    metadata = {
      name      = "metabase-instances"
      namespace = var.kube_namespace_name

      annotations = {
        "networking.gke.io/certmap" : var.certificate_map_name
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
        {
          type  = "NamedAddress"
          value = google_compute_global_address.default.name
        }
      ]
    }
  }
}

# https://cloud.google.com/kubernetes-engine/docs/how-to/configure-gateway-resources#configure_ssl_policies
resource "kubernetes_manifest" "gateway_policy" {
  manifest = {
    apiVersion = "networking.gke.io/v1"
    kind       = "GCPGatewayPolicy"
    metadata = {
      name      = "metabase-instances"
      namespace = var.kube_namespace_name
    }

    spec = {
      default = {
        sslPolicy = var.ssl_policy_name
      }

      targetRef = {
        group = "gateway.networking.k8s.io"
        kind  = "Gateway"
        name  = kubernetes_manifest.gateway.manifest.metadata.name
      }
    }
  }
}

resource "kubernetes_manifest" "instances_backend_policy" {
  for_each = var.metabase_instances

  manifest = {
    apiVersion = "networking.gke.io/v1"
    kind       = "GCPBackendPolicy"
    metadata = {
      name      = "mb-${each.value.metabase_instance_id}"
      namespace = var.kube_namespace_name
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
        name  = kubernetes_service.instances[each.key].metadata[0].name
      }
    }
  }
}

resource "kubernetes_manifest" "instances_httproute" {
  for_each = var.metabase_instances

  manifest = {
    apiVersion = "gateway.networking.k8s.io/v1beta1"
    kind       = "HTTPRoute"
    metadata = {
      name      = "mb-${each.key}"
      namespace = var.kube_namespace_name
    }

    spec = {
      parentRefs = [
        {
          name = kubernetes_manifest.gateway.manifest.metadata.name
        }
      ]

      hostnames = [
        "${each.value.metabase_instance_id}.${local.domain}"
      ]

      rules = [
        {
          # No path matching is specified, so all traffic is routed to this backend.
          backendRefs = [
            {
              name = kubernetes_service.instances[each.key].metadata[0].name
              port = kubernetes_service.instances[each.key].spec[0].port[0].port
            }
          ]
        }
      ]
    }
  }
}
