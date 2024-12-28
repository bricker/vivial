module "iap_app_kubernetes_service" {
  source       = "../../modules/kube_service"
  namespace    = var.kube_namespace_name
  service_name = local.iap_service_name
  service_port = local.service_port
  app_name = local.app_name
  app_port     = local.app_port
}

module "iap_service_backend_policy" {
  source = "../../modules/backend_policy"

  name      = local.iap_service_name
  namespace = var.kube_namespace_name
  service_name                      = module.kubernetes_service_iap.name
  iap_oauth_client_kube_secret_name = var.iap_oauth_client_kube_secret_name
  iap_oauth_client_id               = var.iap_oauth_client_id
  iap_enabled                       = true # always enabled for this service
}
