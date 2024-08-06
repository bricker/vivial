module "app_gateway" {
  depends_on = [ google_compute_global_address.a_addrs ]
  source       = "../../modules/app_gateway"
  service_name = module.kubernetes_service.name
  labels = {
    app = local.app_name
  }
  namespace            = var.kube_namespace_name
  certificate_map_name = var.certificate_map_name
  global_address_names         = [for addr in google_compute_global_address.a_addrs: addr.name]
  ssl_policy_name      = var.ssl_policy_name
}

module "gateway_backend_policy" {
  source = "../../modules/gateway_backend_policy"

  name      = local.app_name
  namespace = var.kube_namespace_name
  labels = {
    app = local.app_name
  }
  service_name                 = module.kubernetes_service.name
  iap_oauth_client_kube_secret_name = var.iap_oauth_client_kube_secret_name
  iap_oauth_client_id = var.iap_oauth_client_id
  iap_enabled = var.iap_enabled
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
                  }
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
