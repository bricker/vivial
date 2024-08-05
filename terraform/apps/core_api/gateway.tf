module "app_gateway" {
  source       = "../../modules/app_gateway"
  service_name = module.kubernetes_service.name
  labels = {
    app = local.app_name
  }
  namespace            = var.kube_namespace_name
  certificate_map_name = var.certificate_map_name
  global_address_name         = google_compute_global_address.default.name
  ssl_policy_name      = var.ssl_policy_name
}


resource "kubernetes_manifest" "app_httproute" {
  manifest = {
    apiVersion = "gateway.networking.k8s.io/v1beta1"
    kind       = "HTTPRoute"
    metadata = {
      name      = local.app_name
      namespace = var.kube_namespace_name

      labels = {
        app = local.app_name
      }
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
                type  = "PathPrefix"
                value = "/oauth"
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
                    name  = "eave-lb-geo-region"
                    value = "{client_region}"
                  },
                  {
                    name  = "eave-lb-geo-subdivision"
                    value = "{client_region_subdivision}"
                  },
                  {
                    name  = "eave-lb-geo-city"
                    value = "{client_city}"
                  },
                  {
                    name  = "eave-lb-geo-coordinates"
                    value = "{client_city_lat_long}"
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
