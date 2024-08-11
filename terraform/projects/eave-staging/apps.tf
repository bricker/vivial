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

  LOG_LEVEL        = "DEBUG"
  release_version  = "latest"
  EAVE_CREDENTIALS = var.INTERNAL_EAVE_CREDENTIALS

  cloudsql_user_role_id = module.project_base.cloudsql_user_role_id
  impersonator_role_id  = module.project_base.impersonator_role_id
  impersonators = [
    "serviceAccount:${google_service_account.cloudsql_bastion_sa.email}",
  ]
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
  EAVE_CREDENTIALS                  = var.INTERNAL_EAVE_CREDENTIALS
  iap_oauth_client_id               = var.IAP_OAUTH_CLIENT_ID
  iap_oauth_client_kube_secret_name = module.shared_kubernetes_resources.iap_oauth_client_kube_secret_name
  iap_enabled                       = true
}

module "playground_todoapp" {
  source                 = "../../apps/playground_todoapp"
  cloudsql_instance_name = module.cloudsql_eave_core.cloudsql_instance_name
  docker_repository_ref  = module.project_base.docker_repository_ref
  ssl_policy_name        = module.project_base.ssl_policy_name
  certificate_map_name   = module.project_base.certificate_map_name
  kube_namespace_name    = module.shared_kubernetes_resources.eave_namespace_name
  shared_config_map_name = module.shared_kubernetes_resources.shared_config_map_name

  dns_zone_name = module.dns_zone_blue.dns_zone_name

  cdn_base_url                      = module.cdn.url
  LOG_LEVEL                         = "DEBUG"
  release_version                   = "latest"
  EAVE_CREDENTIALS                  = var.PLAYGROUND_TODOAPP_EAVE_CREDENTIALS
  iap_oauth_client_id               = var.IAP_OAUTH_CLIENT_ID
  iap_oauth_client_kube_secret_name = module.shared_kubernetes_resources.iap_oauth_client_kube_secret_name

  cloudsql_user_role_id = module.project_base.cloudsql_user_role_id
  impersonator_role_id  = module.project_base.impersonator_role_id
  impersonators = [
    "serviceAccount:${google_service_account.cloudsql_bastion_sa.email}",
  ]
}

module "playground_quizapp" {
  source                 = "../../apps/playground_quizapp"
  docker_repository_ref  = module.project_base.docker_repository_ref
  ssl_policy_name        = module.project_base.ssl_policy_name
  certificate_map_name   = module.project_base.certificate_map_name
  kube_namespace_name    = module.shared_kubernetes_resources.eave_namespace_name
  shared_config_map_name = module.shared_kubernetes_resources.shared_config_map_name

  dns_zone_name                     = module.dns_zone_red.dns_zone_name
  cdn_base_url                      = module.cdn.url
  LOG_LEVEL                         = "DEBUG"
  release_version                   = "latest"
  EAVE_CREDENTIALS                  = var.PLAYGROUND_QUIZAPP_EAVE_CREDENTIALS
  iap_oauth_client_id               = var.IAP_OAUTH_CLIENT_ID
  iap_oauth_client_kube_secret_name = module.shared_kubernetes_resources.iap_oauth_client_kube_secret_name
}
