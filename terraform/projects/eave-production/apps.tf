module "shared_kubernetes_resources" {
  source                   = "../../modules/kube_shared_resources"
  iap_oauth_client_secret  = module.iap.google_iap_client.secret
  dns_domain               = local.dns_domain
  www_public_domain_prefix = local.www_public_domain_prefix
  api_public_domain_prefix = local.api_public_domain_prefix
  STRIPE_ENVIRONMENT       = local.STRIPE_ENVIRONMENT
}

module "core_api_app" {
  source = "../../apps/core_api"

  public_domain_prefix = local.api_public_domain_prefix

  google_sql_database_instance               = module.cloudsql_eave_core.google_sql_database_instance
  google_dns_managed_zone                    = module.dns_zone_base_domain.google_dns_managed_zone
  google_compute_ssl_policy                  = module.project_base.google_compute_ssl_policy
  google_certificate_manager_certificate_map = module.project_base.google_certificate_manager_certificate_map
  google_compute_network                     = module.project_base.google_compute_network
  google_compute_subnetwork                  = module.project_base.google_compute_subnetwork
  google_kms_crypto_key_jws_signing_key      = module.project_base.google_kms_crypto_key_jws_signing_key

  docker_repository_ref  = module.project_base.docker_repository_ref
  kube_namespace_name    = module.shared_kubernetes_resources.eave_namespace_name
  shared_config_map_name = module.shared_kubernetes_resources.shared_config_map_name

  impersonator_role_name         = module.project_base.impersonator_role_name
  compute_oslogin_role_name      = module.project_base.compute_oslogin_role_name
  service_account_user_role_name = module.project_base.service_account_user_role_name

  bastion_accessors = [
    # TODO: Make this a group, like `devops@eave.fyi` or something
    "user:bryan@eave.fyi",
    "user:liam@eave.fyi",
  ]

  LOG_LEVEL                    = "DEBUG"
  release_version              = "latest"
  JWS_SIGNING_KEY_VERSION_PATH = module.project_base.kms_jws_signing_key_default_version_id

  iap_enabled                       = false
  iap_oauth_client_id               = module.iap.google_iap_client.client_id
  iap_oauth_client_kube_secret_name = module.shared_kubernetes_resources.iap_oauth_client_kube_secret_name
  iap_jwt_aud = "/projects/${data.google_project.default.number}/global/backendServices/${local.iap_gateways["core_iap"]}"
}

module "dashboard_app" {
  source = "../../apps/dashboard"

  public_domain_prefix = local.www_public_domain_prefix

  google_dns_managed_zone                    = module.dns_zone_base_domain.google_dns_managed_zone
  google_compute_ssl_policy                  = module.project_base.google_compute_ssl_policy
  google_certificate_manager_certificate_map = module.project_base.google_certificate_manager_certificate_map
  docker_repository_ref                      = module.project_base.docker_repository_ref
  kube_namespace_name                        = module.shared_kubernetes_resources.eave_namespace_name
  shared_config_map_name                     = module.shared_kubernetes_resources.shared_config_map_name

  cdn_base_url    = module.cdn.url
  LOG_LEVEL       = "DEBUG"
  release_version = "latest"

  iap_enabled                       = false
  iap_oauth_client_id               = module.iap.google_iap_client.client_id
  iap_oauth_client_kube_secret_name = module.shared_kubernetes_resources.iap_oauth_client_kube_secret_name
}

module "admin_app" {
  source = "../../apps/admin"

  public_domain_prefix = local.admin_public_domain_prefix

  google_dns_managed_zone                    = module.dns_zone_base_domain.google_dns_managed_zone
  google_compute_ssl_policy                  = module.project_base.google_compute_ssl_policy
  google_certificate_manager_certificate_map = module.project_base.google_certificate_manager_certificate_map
  docker_repository_ref                      = module.project_base.docker_repository_ref
  kube_namespace_name                        = module.shared_kubernetes_resources.eave_namespace_name
  shared_config_map_name                     = module.shared_kubernetes_resources.shared_config_map_name

  cdn_base_url    = module.cdn.url
  LOG_LEVEL       = "DEBUG"
  release_version = "latest"

  iap_oauth_client_id               = module.iap.google_iap_client.client_id
  iap_oauth_client_kube_secret_name = module.shared_kubernetes_resources.iap_oauth_client_kube_secret_name
  iap_jwt_aud = "/projects/${data.google_project.default.number}/global/backendServices/${local.iap_gateways["admin"]}"
}
