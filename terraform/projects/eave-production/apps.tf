module "shared_kubernetes_resources" {
  source                  = "../../modules/kube_shared_resources"
  iap_client_ref = module.iap_client.iap_client_ref
  root_domain = local.root_domain
}

module "core_api_app" {
  source  = "../../apps/core_api"
  cloudsql_instance_name = module.cloudsql_eave_core.cloudsql_instance_name
  dns_zone_name               = module.dns_zone_base_domain.dns_zone_name
  docker_repository_ref      = module.project_base.docker_repository_ref
  ssl_policy_name        = module.project_base.ssl_policy_name
  certificate_map_name   = module.project_base.certificate_map_name
  kube_namespace_name    = module.shared_kubernetes_resources.eave_namespace_name
  shared_config_map_name = module.shared_kubernetes_resources.shared_config_map_name

  LOG_LEVEL = "DEBUG"
  release_version = "latest"
  EAVE_CREDENTIALS = var.INTERNAL_EAVE_CREDENTIALS
}

module "dashboard_app" {
  source  = "../../apps/dashboard"
  dns_zone_name               = module.dns_zone_base_domain.dns_zone_name
  docker_repository_ref      = module.project_base.docker_repository_ref
  ssl_policy_name        = module.project_base.ssl_policy_name
  certificate_map_name   = module.project_base.certificate_map_name
  kube_namespace_name    = module.shared_kubernetes_resources.eave_namespace_name
  shared_config_map_name = module.shared_kubernetes_resources.shared_config_map_name

  cdn_base_url         = "https://${module.cdn.domain}"
  LOG_LEVEL = "DEBUG"
  release_version = "latest"
  EAVE_CREDENTIALS = var.INTERNAL_EAVE_CREDENTIALS
  iap_client_ref = module.iap_client.iap_client_ref
  iap_client_kube_secret_name = module.shared_kubernetes_resources.iap_client_kube_secret_name
  iap_enabled = false
}