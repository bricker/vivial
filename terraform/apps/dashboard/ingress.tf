# resource "kubernetes_manifest" "managed_certificate" {
#   manifest = {
#     apiVersion = "networking.gke.io/v1"
#     kind       = "ManagedCertificate"
#     metadata = {
#       name = local.app_name
#       namespace = var.kube_namespace_name

#       labels = {
#         app = local.app_name
#       }
#     }

#     spec = {
#       domains = [
#         local.domain
#       ]
#     }
#   }
# }

# resource "kubernetes_manifest" "frontend_config" {
#   # Standard app frontend config.
#   manifest = {
#     apiVersion = "networking.gke.io/v1beta1"
#     kind       = "FrontendConfig"
#     metadata = {
#       name = local.app_name
#       namespace = var.kube_namespace_name

#       labels = {
#         app = local.app_name
#       }
#     }

#     spec = {
#       redirectToHttps = {
#         enabled = true
#         responseCodeName = "MOVED_PERMANENTLY_DEFAULT"
#       }
#     }
#   }
# }

# resource "kubernetes_manifest" "backend_config" {
#   # Standard app healthcheck/backend config
#   # Assumes the app is listening on port 8000 and has a /status endpoint.
#   # Also:
#   # - Removes any "server" response header, for security.
#   # - Adds a special header to indicate to the backend that the request flowed through this ingress.

#   manifest = {
#     apiVersion = "cloud.google.com/v1"
#     kind       = "BackendConfig"
#     metadata = {
#       name = local.app_name
#       namespace = var.kube_namespace_name

#       labels = {
#         app = local.app_name
#       }
#     }

#     spec = {
#       healthCheck = {
#         type = "HTTP"
#         requestPath = "/status"
#         port = local.app_port.number
#       }

#       logging = {
#         enable = true
#         sampleRate = 0.5
#       }

#       customRequestHeaders = {
#         headers = [
#           "eave-lb: 1"
#         ]
#       }

#       customResponseHeaders = {
#         headers = [
#           "server: n/a"
#         ]
#       }
#     }
#   }
# }

# resource "kubernetes_ingress_v1" "app" {
#   metadata {
#     name = local.app_name
#     namespace = var.kube_namespace_name
#     annotations = {
#       "networking.gke.io/v1beta1.FrontendConfig" = kubernetes_manifest.frontend_config.manifest.metadata.name
#       "networking.gke.io/managed-certificates" = kubernetes_manifest.managed_certificate.manifest.metadata.name
#       "kubernetes.io/ingress.global-static-ip-name" = google_compute_global_address.default.name
#       "kubernetes.io/ingress.class" = "gce"
#     }

#     labels = {
#       app = local.app_name
#     }
#   }

#   spec {
#     ingress_class_name = "gce"

#     # Default backend doesn't do host matching
#     # default_backend {
#     #   service {
#     #     name = kubernetes_service.app.metadata[0].name
#     #     port {
#     #       name = local.service_port.name
#     #     }
#     #   }
#     # }

#     rule {
#       host = local.domain
#       http {
#         path {
#           path = "/"
#           path_type = "Prefix"
#           backend {
#             service {
#               name = kubernetes_service.app.metadata[0].name
#               port {
#                 name = local.service_port.name
#               }
#             }
#           }
#         }
#       }
#     }
#   }
# }