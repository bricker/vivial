module "shared_kubernetes_resources" {
  depends_on = [module.gke_primary]

  source                     = "../../modules/kube_shared_resources"
  google_project             = data.google_project.default
  dns_domain                 = local.dns_domain
  www_public_domain_prefix   = local.www_public_domain_prefix
  api_public_domain_prefix   = local.api_public_domain_prefix
  admin_public_domain_prefix = local.admin_public_domain_prefix
  STRIPE_ENVIRONMENT         = local.STRIPE_ENVIRONMENT
  EAVE_ENV                   = local.EAVE_ENV
  GOOGLE_MAPS_APIS_DISABLED  = local.GOOGLE_MAPS_APIS_DISABLED
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
  bastion_accessors              = ["group:developers@eave.fyi"]

  LOG_LEVEL                    = "DEBUG"
  release_version              = "latest"
  JWS_SIGNING_KEY_VERSION_PATH = module.project_base.kms_jws_signing_key_default_version_id

  root_iap_enabled     = true
  root_iap_jwt_aud     = "/projects/${data.google_project.default.number}/global/backendServices/${data.google_compute_backend_service.k8s_backend_services["core-api"].generated_id}"
  internal_iap_jwt_aud = "/projects/${data.google_project.default.number}/global/backendServices/${data.google_compute_backend_service.k8s_backend_services["core-api-iap"].generated_id}"

  eventbrite_filler_cron_schedule = "0 10 * * 1" # Mondays at 2/3am PT
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

  iap_enabled                       = true
  iap_jwt_aud                       = "/projects/${data.google_project.default.number}/global/backendServices/${data.google_compute_backend_service.k8s_backend_services["dashboard"].generated_id}"
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

  iap_jwt_aud                       = "/projects/${data.google_project.default.number}/global/backendServices/${data.google_compute_backend_service.k8s_backend_services["admin"].generated_id}"
}
