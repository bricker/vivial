module "app_gateway" {
  depends_on                                 = [google_compute_global_address.a_addrs]
  source                                     = "../../modules/app_gateway"
  service_name                               = module.kubernetes_service.name
  namespace                                  = var.kube_namespace_name
  google_certificate_manager_certificate_map = var.google_certificate_manager_certificate_map
  google_compute_ssl_policy                  = var.google_compute_ssl_policy
  global_address_names                       = [for addr in google_compute_global_address.a_addrs : addr.name]
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
          # No path matching is specified, so all traffic is routed to this backend.
          backendRefs = [
            {
              name = module.healthchecks_kubernetes_service.name
              port = module.healthchecks_kubernetes_service.port.number
            }
          ]
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
        },
        {
          # No path matching is specified, so all traffic is routed to this backend.
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
