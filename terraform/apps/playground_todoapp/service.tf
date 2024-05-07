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

resource "kubernetes_service" "app" {
  metadata {
    name = local.app_name
    namespace = var.kube_namespace_name
    annotations = {
      "beta.cloud.google.com/backend-config" = jsonencode({"default": kubernetes_manifest.backend_config.manifest.metadata.name})
    }

    labels = {
      app = local.app_name
    }
  }

  spec {
    selector = {
      app = local.app_name
    }

    type = "NodePort"
    port {
      name = local.service_port.name
      port = local.service_port.number
      protocol = "TCP"
      target_port = local.app_port.name
    }
  }
}
