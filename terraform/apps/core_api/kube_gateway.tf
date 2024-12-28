module "app_gateway" {
  depends_on   = [google_compute_global_address.a_addrs]
  source       = "../../modules/app_gateway"
  service_name = module.kubernetes_service.name
  namespace                                  = var.kube_namespace_name
  google_certificate_manager_certificate_map = var.google_certificate_manager_certificate_map
  global_address_names                       = [for addr in google_compute_global_address.a_addrs : addr.name]
  google_compute_ssl_policy                  = var.google_compute_ssl_policy
}

module "gateway_backend_policy" {
  source = "../../modules/gateway_backend_policy"

  name      = local.app_name
  namespace = var.kube_namespace_name
  labels = {
    app = local.app_name
  }
  service_name                      = module.kubernetes_service.name
  iap_oauth_client_kube_secret_name = var.iap_oauth_client_kube_secret_name
  iap_oauth_client_id               = var.iap_oauth_client_id
  iap_enabled                       = var.iap_enabled
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
                type  = "PathPrefix"
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
