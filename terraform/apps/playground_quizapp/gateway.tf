module "app_gateway" {
  source       = "../../modules/app_gateway"
  service_name = module.kubernetes_service.name
  labels = {
    app = local.app_name
  }
  namespace            = var.kube_namespace_name
  certificate_map_name = var.certificate_map_name
  address_name         = google_compute_global_address.default.name
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
                add = [
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

# resource "kubernetes_manifest" "backend_policy" {
#   manifest = {
#     apiVersion = "networking.gke.io/v1"
#     kind       = "GCPBackendPolicy"
#     metadata = {
#       name      = local.app_name
#       namespace = var.kube_namespace_name
#     }

#     spec = {
#       default = {
#         # https://cloud.google.com/kubernetes-engine/docs/how-to/configure-gateway-resources#configure_iap
#         iap = {
#           enabled = true
#           oauth2ClientSecret = {
#             name = var.iap_oauth_client_secret_name
#           }
#           clientID = var.iap_oauth_client_id
#         }

#       }

#       targetRef = {
#         group = ""
#         kind  = "Service"
#         name  = kubernetes_service.metadata[0].name
#       }
#     }
#   }
# }