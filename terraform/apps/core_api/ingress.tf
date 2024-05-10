resource "kubernetes_manifest" "managed_certificate" {
  manifest = {
    apiVersion = "networking.gke.io/v1"
    kind       = "ManagedCertificate"
    metadata = {
      name = local.app_name
      namespace = var.kube_namespace_name

      labels = {
        app = local.app_name
      }
    }

    spec = {
      domains = [
        local.domain
      ]
    }
  }
}

resource "kubernetes_manifest" "frontend_config" {
  # Standard app frontend config.
  manifest = {
    apiVersion = "networking.gke.io/v1beta1"
    kind       = "FrontendConfig"
    metadata = {
      name = local.app_name
      namespace = var.kube_namespace_name

      labels = {
        app = local.app_name
      }
    }

    spec = {
      redirectToHttps = {
        enabled = true
        responseCodeName = "MOVED_PERMANENTLY_DEFAULT"
      }
    }
  }
}

resource "kubernetes_manifest" "backend_config" {
  # Standard app healthcheck/backend config
  # Assumes the app is listening on port 8000 and has a /status endpoint.
  # Also:
  # - Removes any "server" response header, for security.
  # - Adds a special header to indicate to the backend that the request flowed through this ingress.

  manifest = {
    apiVersion = "cloud.google.com/v1"
    kind       = "BackendConfig"
    metadata = {
      name = local.app_name
      namespace = var.kube_namespace_name

      labels = {
        app = local.app_name
      }
    }

    spec = {
      healthCheck = {
        type = "HTTP"
        requestPath = "/status"
        port = local.app_port.number
      }

      logging = {
        enable = true
        sampleRate = 0.5
      }

      customRequestHeaders = {
        headers = [
          "eave-lb: 1"
        ]
      }

      customResponseHeaders = {
        headers = [
          "server: n/a"
        ]
      }
    }
  }
}

resource "kubernetes_ingress_v1" "app" {
  metadata {
    name = local.app_name
    namespace = var.kube_namespace_name
    annotations = {
      "networking.gke.io/v1beta1.FrontendConfig" = kubernetes_manifest.frontend_config.manifest.metadata.name
      "networking.gke.io/managed-certificates" = kubernetes_manifest.managed_certificate.manifest.metadata.name
      "kubernetes.io/ingress.global-static-ip-name" = google_compute_global_address.default.name
      "kubernetes.io/ingress.class" = "gce"
    }

    labels = {
      app = local.app_name
    }
  }

  spec {
    ingress_class_name = "gce"

    # The NOOP service is meant to always fail. It prevents external traffic from accessing paths that aren't whitelisted here.
    # GKE provides a "default-http-backend" service that is used if defaultBackend isn't specified here.
    # However, the response that it returns is a 404 with a message that exposes details about the infrastructure, and is therefore unsuitable.
    # default_backend {
    #   service {
    #     name = "noop"
    #     port {
    #       number = 65535
    #     }
    #   }
    # }


    rule {
      host = local.domain
      http {
        # Supported public endpoint prefixes.
        # Everything else is only accessible from the cluster.
        # TODO: a better place to define these?

        path {
          path = "/status"
          path_type = "Prefix"
          backend {
            service {
              name = kubernetes_service.app.metadata[0].name
              port {
                name = kubernetes_service.app.spec[0].port[0].name
              }
            }
          }
        }
        path {
          path = "/healthz"
          path_type = "Exact"
          backend {
            service {
              name = kubernetes_service.app.metadata[0].name
              port {
                name = kubernetes_service.app.spec[0].port[0].name
              }
            }
          }
        }
        path {
          path = "/public"
          path_type = "Prefix"
          backend {
            service {
              name = kubernetes_service.app.metadata[0].name
              port {
                name = kubernetes_service.app.spec[0].port[0].name
              }
            }
          }
        }
        path {
          path = "/oauth"
          path_type = "Prefix"
          backend {
            service {
              name = kubernetes_service.app.metadata[0].name
              port {
                name = kubernetes_service.app.spec[0].port[0].name
              }
            }
          }
        }
        path {
          path = "/favicon.ico"
          path_type = "Exact"
          backend {
            service {
              name = kubernetes_service.app.metadata[0].name
              port {
                name = kubernetes_service.app.spec[0].port[0].name
              }
            }
          }
        }
      }
    }
  }
}