# This module defines the service that is publicly accessible (not behind IAP) to expose the healthcheck endpoints.
# Because GCP Monitoring Uptime Checks OIDC auth wasn't working

module "healthchecks_kubernetes_service" {
  source       = "../../modules/kube_service"
  namespace    = var.kube_namespace_name
  service_name = "${local.app_name}-healthchecks"
  service_port = local.service_port
  app_name     = local.app_name
  app_port     = local.app_port
}

module "healthcheck_service_backend_policy" {
  source = "../../modules/backend_policy"

  name                              = module.healthchecks_kubernetes_service.name
  namespace                         = var.kube_namespace_name
  service_name                      = module.healthchecks_kubernetes_service.name
  iap_oauth_client_kube_secret_name = var.iap_oauth_client_kube_secret_name
  iap_oauth_client_id               = var.iap_oauth_client_id
  iap_enabled                       = false # IAP is always disabled for healthcheck endpoints
}
