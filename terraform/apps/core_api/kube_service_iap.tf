module "iap_app_kubernetes_service" {
  source       = "../../modules/kube_service"
  namespace    = var.kube_namespace_name
  service_name = "${local.app_name}-iap"
  service_port = local.service_port
  app_name     = local.app_name
  app_port     = local.app_port
  iap_oauth_client_kube_secret_name = var.iap_oauth_client_kube_secret_name
  iap_oauth_client_id               = var.iap_oauth_client_id
  iap_enabled                       = true # always enabled for this service
}

moved {
  from = module.iap_service_backend_policy.kubernetes_manifest.backend_policy
  to   = module.iap_app_kubernetes_service.kubernetes_manifest.backend_policy
}
