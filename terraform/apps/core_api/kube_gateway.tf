module "app_gateway" {
  depends_on                                 = [google_compute_global_address.a_addrs]
  source                                     = "../../modules/app_gateway"
  service_name                               = module.kubernetes_service.name
  namespace                                  = var.kube_namespace_name
  google_certificate_manager_certificate_map = var.google_certificate_manager_certificate_map
  global_address_names                       = [for addr in google_compute_global_address.a_addrs : addr.name]
  google_compute_ssl_policy                  = var.google_compute_ssl_policy
}

resource "kubernetes_manifest" "app_httproute" {
  lifecycle {
    prevent_destroy = true
  }

  manifest = {
    apiVersion = "gateway.networking.k8s.io/v1beta1"
    kind       = "HTTPRoute"
    metadata = {
      name      = local.app_name
      namespace = var.kube_namespace_name
    }

    spec = {
      parentRefs = [
        {
          name = module.app_gateway.name
        }
      ]

      hostnames = [
        local.domain
      ]

      rules = [
        {
          # These are the only path prefixes that can be accessed through the load balancer.
          # All other path prefixes are considered internal-only and can only be accessed within the cluster.
          matches = [
            {
              path = {
                type  = "Exact"
                value = "/status"
              }
            },
            {
              path = {
                type  = "Exact"
                value = "/healthz"
              }
            },
            {
              path = {
                type  = "PathPrefix"
                value = "/public"
              }
            },
            {
              path = {
                type  = "Exact"
                value = "/graphql"
              }
            },
            {
              path = {
                type  = "Exact"
                value = "/favicon.ico"
              }
            }
          ]

          backendRefs = [
            {
              name = module.kubernetes_service.name
              port = module.kubernetes_service.port.number
            }
          ]

          filters = [
            {
              type = "RequestHeaderModifier"
              requestHeaderModifier = {
                set = [
                  {
                    name  = "eave-lb"
                    value = "1"
                  },
                  {
                    name  = "eave-lb-client-ip"
                    value = "{client_ip_address}"
                  },
                ]
              }
            },
            {
              type = "ResponseHeaderModifier"
              responseHeaderModifier = {
                set = [
                  {
                    name  = "server"
                    value = "n/a"
                  }
                ]
              }
            }
          ]
        },
        {
          # Anything matching these rules go through the IAP-enabled service
          matches = [
            {
              path = {
                type  = "PathPrefix"
                value = "/iap"
              }
            },
          ]

          backendRefs = [
            {
              name = module.iap_app_kubernetes_service.name
              port = module.iap_app_kubernetes_service.port.number
            }
          ]

          filters = [
            {
              type = "RequestHeaderModifier"
              requestHeaderModifier = {
                set = [
                  {
                    name  = "eave-lb"
                    value = "1"
                  },
                  {
                    name  = "eave-lb-client-ip"
                    value = "{client_ip_address}"
                  },
                ]
              }
            },
            {
              type = "ResponseHeaderModifier"
              responseHeaderModifier = {
                set = [
                  {
                    name  = "server"
                    value = "n/a"
                  }
                ]
              }
            }
          ]
        }
      ]
    }
  }
}
