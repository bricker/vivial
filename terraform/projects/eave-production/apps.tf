module "shared_kubernetes_resources" {
  source                        = "../../modules/kube_shared_resources"
  iap_oauth_client_secret       = var.IAP_OAUTH_CLIENT_SECRET
  root_domain                   = local.root_domain
  eave_slack_signups_channel_id = local.eave_slack_signups_channel_id
}

module "core_api_app" {
  source                 = "../../apps/core_api"
  cloudsql_instance_name = module.cloudsql_eave_core.cloudsql_instance_name
  dns_zone_name          = module.dns_zone_base_domain.dns_zone_name
  docker_repository_ref  = module.project_base.docker_repository_ref
  ssl_policy_name        = module.project_base.ssl_policy_name
  certificate_map_name   = module.project_base.certificate_map_name
  kube_namespace_name    = module.shared_kubernetes_resources.eave_namespace_name
  shared_config_map_name = module.shared_kubernetes_resources.shared_config_map_name

  impersonator_role_name        = module.project_base.impersonator_role_name
  compute_oslogin_role_name = module.project_base.compute_oslogin_role_name
  service_account_user_role_name = module.project_base.service_account_user_role_name
  network_name                  = module.project_base.network_name
  subnetwork_self_link          = module.project_base.subnetwork_self_link
  bastion_accessors             = ["user:bryan@eave.fyi"]

  LOG_LEVEL        = "DEBUG"
  release_version  = "latest"
  EAVE_CREDENTIALS = var.INTERNAL_EAVE_CREDENTIALS
}

module "dashboard_app" {
  source                 = "../../apps/dashboard"
  dns_zone_name          = module.dns_zone_base_domain.dns_zone_name
  docker_repository_ref  = module.project_base.docker_repository_ref
  ssl_policy_name        = module.project_base.ssl_policy_name
  certificate_map_name   = module.project_base.certificate_map_name
  kube_namespace_name    = module.shared_kubernetes_resources.eave_namespace_name
  shared_config_map_name = module.shared_kubernetes_resources.shared_config_map_name

  cdn_base_url     = module.cdn.url
  LOG_LEVEL        = "DEBUG"
  release_version  = "latest"
  EAVE_CREDENTIALS = var.INTERNAL_EAVE_CREDENTIALS
  iap_enabled      = false
}