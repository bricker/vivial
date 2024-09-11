resource "kubernetes_namespace" "eave" {
  metadata {
    name = "eave"
  }
}

resource "kubernetes_config_map" "shared" {
  metadata {
    name      = "shared"
    namespace = kubernetes_namespace.eave.metadata[0].name
  }

  data = {
    GOOGLE_CLOUD_PROJECT = data.google_project.default.project_id
    EAVE_ENV             = "production"

    EAVE_BASE_URL_PUBLIC           = "https://${var.root_domain}"
    EAVE_BASE_URL_INTERNAL         = "http://${kubernetes_namespace.eave.metadata[0].name}.svc.cluster.local"
    EAVE_API_BASE_URL_PUBLIC       = "https://api.${var.root_domain}"
    EAVE_API_BASE_URL_INTERNAL     = "http://core-api.${kubernetes_namespace.eave.metadata[0].name}.svc.cluster.local"
    EAVE_DASHBOARD_BASE_URL_PUBLIC = "https://dashboard.${var.root_domain}"
    # EAVE_INGEST_BASE_URL           = "http://core-api.${kubernetes_namespace.eave.metadata[0].name}.svc.cluster.local"

    EAVE_SLACK_SIGNUPS_CHANNEL_ID = var.eave_slack_signups_channel_id
  }
}


# This is for Gateway IAP
# Secrets have to be created per-namespace
resource "kubernetes_secret" "iap_oauth_client_secret" {
  for_each = toset([
    kubernetes_namespace.eave.metadata[0].name,
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
