resource "kubernetes_namespace" "eave" {
  metadata {
    name = "eave"
  }
}

output "eave_namespace_name" {
  value = kubernetes_namespace.eave.name
}

resource "kubernetes_namespace" "metabase" {
  metadata {
    name = "metabase"
  }
}

output "metabase_namespace_name" {
  value = kubernetes_namespace.metabase.name
}

resource "kubernetes_config_map" "shared" {
  metadata {
    name = "shared-configmap"
    namespace = kubernetes_namespace.eave.metadata.0.name
  }

  data = {
    GOOGLE_CLOUD_PROJECT = "${var.project_id}"
    EAVE_METABASE_BASE_PUBLIC = "https://metabase.${var.root_domain}"
    EAVE_METABASE_BASE_INTERNAL = "http://metabase.${kubernetes_namespace.eave.metadata.0.name}.svc.cluster.local"

    EAVE_API_BASE_PUBLIC = "https://api.${var.root_domain}"
    EAVE_API_BASE_INTERNAL = "http://core-api.${kubernetes_namespace.eave.metadata.0.name}.svc.cluster.local"

    EAVE_DASHBOARD_BASE_PUBLIC = "https://dashboard.${var.root_domain}"
    EAVE_DASHBOARD_BASE_INTERNAL = "http://dashboard.${kubernetes_namespace.eave.metadata.0.name}.svc.cluster.local"

    EAVE_INTERNAL_ROOT_DOMAIN = "${kubernetes_namespace.eave.metadata.0.name}.svc.cluster.local"
    METABASE_INTERNAL_ROOT_DOMAIN = "${kubernetes_namespace.metabase.metadata.0.name}.svc.cluster.local"

    EAVE_COOKIE_DOMAIN = ".${var.root_domain}"
  }
}

output "shared_config_map_name" {
  value = kubernetes_config_map.shared.name
}

resource "kubernetes_service" "noop" {
  # Noop service; always fails.
  # This can be used for default backend in an Ingress when you want to block certain routes from being accessed externally.
  metadata {
    name = "noop"
    namespace = kubernetes_namespace.eave.metadata.0.name
  }

  spec {
    type = "ExternalName"
    external_name = "eave.fyi" # Dummy value
  }
}

resource "kubernetes_manifest" "shared_backend_config" {
  # Standard app healthcheck/backend config
  # Assumes the app is listening on port 8000 and has a /status endpoint.
  # Also:
  # - Removes any "server" response header, for security.
  # - Adds a special header to indicate to the backend that the request flowed through this ingress.

  manifest = {
    apiVersion = "cloud.google.com/v1"
    kind       = "BackendConfig"
    metadata = {
      name = "shared-bc"
      namespace = kubernetes_namespace.eave.metadata.0.name
    }

    spec = {
      healthCheck = {
        type = "HTTP"
        requestPath = "/status"
        port = 8000
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

output "shared_backend_config_name" {
  value = kubernetes_manifest.shared_backend_config.manifest.metadata.name
}

resource "kubernetes_manifest" "shared_frontend_config" {
  # Standard app frontend config.
  manifest = {
    apiVersion = "networking.gke.io/v1beta1"
    kind       = "FrontendConfig"
    metadata = {
      name = "shared-fc"
      namespace = kubernetes_namespace.eave.metadata.0.name
    }

    spec = {
      redirectToHttps = {
        enabled = true
        responseCodeName = "MOVED_PERMANENTLY_DEFAULT"
      }
    }
  }
}


output "shared_frontend_config_name" {
  value = kubernetes_manifest.shared_frontend_config.manifest.metadata.name
}