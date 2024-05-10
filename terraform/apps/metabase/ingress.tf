# resource "kubernetes_manifest" "managed_certificate" {
#   manifest = {
#     apiVersion = "networking.gke.io/v1"
#     kind       = "ManagedCertificate"
#     metadata = {
#       name = "metabase-instances"
#       namespace = var.kube_namespace_name
#     }

#     spec = {
#       # NOTE: This supports a maximum of 100 domains.
#       # To support wildcard domains, a Certificate Map is necessary.
#       domains = [
#         for instance in var.metabase_instances: "${instance.metabase_instance_id}.${local.domain}"
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
#       name = "frontend-config"
#       namespace = var.kube_namespace_name
#     }

#     spec = {
#       redirectToHttps = {
#         enabled = true
#         responseCodeName = "MOVED_PERMANENTLY_DEFAULT"
#       }
#     }
#   }
# }

# resource "kubernetes_ingress_v1" "metabase_instances" {
#   metadata {
#     name = "metabase-instances"
#     namespace = var.kube_namespace_name
#     annotations = {
#       "networking.gke.io/v1beta1.FrontendConfig" = kubernetes_manifest.frontend_config.manifest.metadata.name
#       "networking.gke.io/managed-certificates" = kubernetes_manifest.managed_certificate.manifest.metadata.name
#       "kubernetes.io/ingress.global-static-ip-name" = google_compute_global_address.default.name
#       "kubernetes.io/ingress.class" = "gce"
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

#     dynamic "rule" {
#       for_each = { for instance in var.metabase_instances: instance.metabase_instance_id => instance }
#       content {
#         host = "${rule.value.metabase_instance_id}.${local.domain}"
#         http {
#           path {
#             # path = "/"
#             # path_type = "Prefix"
#             backend {
#               service {
#                 name = module.metabase_instances[rule.key].kubernetes_service.metadata[0].name
#                 port {
#                   name = module.metabase_instances[rule.key].kubernetes_service.spec[0].port[0].name
#                 }
#               }
#             }
#           }
#         }
#       }
#     }
#   }
# }