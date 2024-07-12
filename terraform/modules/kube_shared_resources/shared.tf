resource "kubernetes_namespace" "eave" {
  metadata {
    name = "eave"
  }
}

resource "kubernetes_namespace" "metabase" {
  metadata {
    name = "metabase"
  }
}


resource "kubernetes_config_map" "shared" {
  metadata {
    name      = "shared"
    namespace = kubernetes_namespace.eave.metadata[0].name
  }

  data = {
    GOOGLE_CLOUD_PROJECT = var.project.id

    EAVE_BASE_URL_PUBLIC           = "https://${var.project.root_domain}"
    EAVE_BASE_URL_INTERNAL         = "http://${kubernetes_namespace.eave.metadata[0].name}.svc.cluster.local"
    EAVE_EMBED_BASE_URL_PUBLIC     = "https://embed.${var.project.root_domain}"
    EAVE_EMBED_BASE_URL_INTERNAL   = "http://${kubernetes_namespace.metabase.metadata[0].name}.svc.cluster.local"
    EAVE_API_BASE_URL_PUBLIC       = "https://api.${var.project.root_domain}"
    EAVE_API_BASE_URL_INTERNAL     = "http://core-api.${kubernetes_namespace.eave.metadata[0].name}.svc.cluster.local"
    EAVE_DASHBOARD_BASE_URL_PUBLIC = "https://dashboard.${var.project.root_domain}"

    EAVE_ENV = "production"
  }
}


# This is for Gateway IAP
# Secrets have to be created per-namespace
resource "kubernetes_secret" "iap_oauth_client_secret" {
  for_each = toset([
    kubernetes_namespace.eave.metadata[0].name,
    kubernetes_namespace.metabase.metadata[0].name
  ])

  metadata {
    name      = "iap-oauth-client-secret"
    namespace = each.value
  }

  type = "Opaque"
  data = {
    key = var.iap_oauth_client_secret
  }
}

# resource "kubernetes_service" "noop" {
#   # Noop service; always fails.
#   # This can be used for default backend in an Ingress when you want to block certain routes from being accessed externally.
#   metadata {
#     name = "noop"
#     namespace = kubernetes_namespace.eave.metadata[0].name
#   }

#   spec {
#     type = "ExternalName"
#     external_name = "eave.fyi" # Dummy value
#   }
# }
