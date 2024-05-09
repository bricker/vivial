# # https://cloud.google.com/kubernetes-engine/docs/concepts/gateway-api



# resource "kubernetes_manifest" "gateway" {
#   manifest = {
#     apiVersion = "gateway.networking.k8s.io/v1beta1"
#     kind       = "Gateway"
#     metadata = {
#       name = "metabase-instances"
#       namespace = var.kube_namespace_name

#       annotations = {
#         "networking.gke.io/certmap": store-example-com-map

#       }
#     }

#     spec = {
#       # https://cloud.google.com/kubernetes-engine/docs/concepts/gateway-api#gatewayclass
#       gatewayClassName = "gke-l7-global-external-managed"
#       listeners = [
#         {
#           name = "https"
#           protocol = "HTTPS"
#           port = 443

#           tls = {
#             mode = "Terminate"
#             options = {
#               "networking.gke.io/pre-shared-certs" = kubernetes_manifest.managed_certificate.manifest.metadata.name
#             }
#           }

#           allowedRoutes = {
#             kinds = [
#               {
#                 kind = "HTTPRoute"
#               }
#             ]
#           }
#         }
#       ]
#     }
#   }
# }


# # https://cloud.google.com/kubernetes-engine/docs/how-to/configure-gateway-resources#configure_ssl_policies
# resource "kubernetes_manifest" "gateway_policy" {
#   manifest = {
#     apiVersion = "networking.gke.io/v1"
#     kind       = "GCPGatewayPolicy"
#     metadata = {
#       name = "metabase-instances"
#       namespace = var.kube_namespace_name
#     }

#     spec = {
#       default = {
#         sslPolicy = var.ssl_policy_name
#       }

#       targetRef = {
#         group = "gateway.networking.k8s.io"
#         kind = "Gateway"
#         name = kubernetes_manifest.gateway.manifest.metadata.name
#       }
#     }
#   }
# }

# resource "kubernetes_manifest" "httproute" {
#   manifest = {
#     apiVersion = "gateway.networking.k8s.io/v1beta1"
#     kind       = "HTTPRoute"
#     metadata = {
#       name = "metabase-instances"
#       namespace = var.kube_namespace_name
#     }

#     spec = {
#       parentRefs = [
#         {
#           name = kubernetes_manifest.gateway.manifest.metadata.name
#         }
#       ]

#       hostname = [
#         module.dns.domain
#       ]

#       rules = [
#         {
#           matches = [
#             {
#               path = {
#                 value = ""
#               }
#             }
#           ]

#           backendRefs = [
#             {
#               name = kubernetes_service.app.metadata[0].name
#               port = kubernetes_service.app.ports[0].http
#             }
#           ]
#         }
#       ]
#     }
#   }
# }