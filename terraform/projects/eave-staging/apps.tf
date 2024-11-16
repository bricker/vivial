module "shared_kubernetes_resources" {
  source                        = "../../modules/kube_shared_resources"
  iap_oauth_client_secret       = var.IAP_OAUTH_CLIENT_SECRET
  dns_domain                   = local.dns_domain
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

  impersonator_role_name         = module.project_base.impersonator_role_name
  compute_oslogin_role_name      = module.project_base.compute_oslogin_role_name
  service_account_user_role_name = module.project_base.service_account_user_role_name
  network_name                   = module.project_base.network_name
  subnetwork_self_link           = module.project_base.subnetwork_self_link
  bastion_accessors              = ["group:developers@eave.fyi"]

  LOG_LEVEL                    = "DEBUG"
  release_version              = "latest"
  SEGMENT_CORE_API_WRITE_KEY   = local.SEGMENT_CORE_API_WRITE_KEY
  JWS_SIGNING_KEY_VERSION_PATH = module.project_base.kms_jws_signing_key_default_version_id
}

module "dashboard_app" {
  source                 = "../../apps/dashboard"
  dns_zone_name          = module.dns_zone_base_domain.dns_zone_name
  docker_repository_ref  = module.project_base.docker_repository_ref
  ssl_policy_name        = module.project_base.ssl_policy_name
  certificate_map_name   = module.project_base.certificate_map_name
  kube_namespace_name    = module.shared_kubernetes_resources.eave_namespace_name
  shared_config_map_name = module.shared_kubernetes_resources.shared_config_map_name

  cdn_base_url                      = module.cdn.url
  LOG_LEVEL                         = "DEBUG"
  release_version                   = "latest"
  iap_enabled                       = true
  iap_oauth_client_id               = var.IAP_OAUTH_CLIENT_ID
  iap_oauth_client_kube_secret_name = module.shared_kubernetes_resources.iap_oauth_client_kube_secret_name
  SEGMENT_WEBSITE_WRITE_KEY         = local.SEGMENT_WEBSITE_WRITE_KEY
}
