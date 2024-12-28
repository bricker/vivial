module "kubernetes_service" {
  source       = "../../modules/kube_service"
  namespace    = var.kube_namespace_name
  service_name = local.app_name
  service_port = local.service_port
  app_port     = local.app_port
}

moved {
  from = module.gateway_backend_policy
  to = module.service_backend_policy
}

module "service_backend_policy" {
  source = "../../modules/backend_policy"

  name      = local.app_name
  namespace = var.kube_namespace_name
  service_name                      = module.kubernetes_service.name
  iap_oauth_client_kube_secret_name = var.iap_oauth_client_kube_secret_name
  iap_oauth_client_id               = var.iap_oauth_client_id
  iap_enabled                       = true # IAP is always enabled for Admin dash
}
