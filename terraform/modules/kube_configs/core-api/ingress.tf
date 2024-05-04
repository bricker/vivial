resource "kubernetes_ingress" "default" {
  metadata {
    name = "${local.app_name}-ingress"
    namespace = local.kube_namespace
    annotations = {
      "networking.gke.io/v1beta1.FrontendConfig": "shared-fc"
      "networking.gke.io/managed-certificates": kubernetes_manifest.managed_certificate.name
      "kubernetes.io/ingress.global-static-ip-name": "api-dot-eave-dot-dev-addr"
      "kubernetes.io/ingress.class": "gce"
    }

    labels = {
      "app" = "${local.app_name}-app"
    }

  }

  spec {
    # This does not work. Without the "ingress.class" annotation, the LB isn't created.
    ingress_class_name = "gce"

    # The NOOP service is meant to always fail. It prevents external traffic from accessing paths that aren't whitelisted here.
    # GKE provides a "default-http-backend" service that is used if defaultBackend isn't specified here.
    # However, the response that it returns is a 404 with a message that exposes details about the infrastructure, and is therefore unsuitable.
    # backend {
    #   service_name = "noop"
    #   service_port = "65535"
    # }

    rule {
      host = "api.${var.root_domain}"
      http {
        # Supported public endpoint prefixes.
        # Everything else is only accessible from the cluster.
        # TODO: a better place to define these?

        path {
          path = "/status"
          backend {
            service_name = local.app_name
            service_port = "http"
          }
        }
        path {
          path = "/public"
          backend {
            service_name = local.app_name
            service_port = "http"
          }
        }
        path {
          path = "/oauth"
          backend {
            service_name = local.app_name
            service_port = "http"
          }
        }
        path {
          path = "/favicon.ico"
          backend {
            service_name = local.app_name
            service_port = "http"
          }
        }
      }
    }
  }
}