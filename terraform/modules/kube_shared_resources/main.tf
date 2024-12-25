resource "kubernetes_namespace" "eave" {
  lifecycle {
    prevent_destroy = true
  }

  metadata {
    name = "eave"
  }
}

resource "kubernetes_config_map" "shared" {
  lifecycle {
    prevent_destroy = true
  }

  metadata {
    name      = "shared"
    namespace = kubernetes_namespace.eave.metadata[0].name
  }

  data = {
    GOOGLE_CLOUD_PROJECT = data.google_project.default.project_id
    EAVE_ENV             = "production"

    EAVE_BASE_URL_PUBLIC           = "https://${var.dns_domain}"
    EAVE_BASE_URL_INTERNAL         = "http://${kubernetes_namespace.eave.metadata[0].name}.svc.cluster.local"
    EAVE_API_BASE_URL_PUBLIC       = "https://${var.api_public_domain_prefix}.${var.dns_domain}"
    EAVE_API_BASE_URL_INTERNAL     = "http://core-api.${kubernetes_namespace.eave.metadata[0].name}.svc.cluster.local"
    EAVE_DASHBOARD_BASE_URL_PUBLIC = "https://${var.www_public_domain_prefix}.${var.dns_domain}"

    STRIPE_ENVIRONMENT = var.STRIPE_ENVIRONMENT
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
