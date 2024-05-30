resource "google_certificate_manager_certificate_map" "default" {
  name = "root-certificate-map"
}

module "core_api_app" {
  source  = "../../apps/core_api"
  project = local.project

  cloudsql_instance_name = module.cloudsql_eave_core.instance.name
  dns_zone               = module.dns_zone_base_domain.zone
  docker_repository      = module.docker_registry.repository
  ssl_policy_name        = module.ssl_policy.policy_name
  certificate_map_name   = google_certificate_manager_certificate_map.default.name

  kube_namespace_name    = module.shared_kubernetes_resources.eave_namespace_name
  shared_config_map_name = module.shared_kubernetes_resources.shared_config_map_name

  LOG_LEVEL = "DEBUG"

  release_date    = "unknown"
  release_version = "latest"

  EAVE_CREDENTIALS = var.INTERNAL_EAVE_CREDENTIALS
}

module "playground_todoapp" {
  source  = "../../apps/playground_todoapp"
  project = local.project

  cloudsql_instance_name = module.cloudsql_eave_core.instance.name
  dns_zone               = module.dns_zone_base_domain.zone
  docker_repository      = module.docker_registry.repository
  ssl_policy_name        = module.ssl_policy.policy_name
  certificate_map_name   = google_certificate_manager_certificate_map.default.name
  cdn_base_url = "https://storage.googleapis.com/${google_storage_bucket.cdn.name}"

  kube_namespace_name    = module.shared_kubernetes_resources.eave_namespace_name
  shared_config_map_name = module.shared_kubernetes_resources.shared_config_map_name

  LOG_LEVEL = "DEBUG"

  release_date    = "unknown"
  release_version = "latest"

  EAVE_CREDENTIALS = var.PLAYGROUND_TODOAPP_EAVE_CREDENTIALS
}

module "dashboard_app" {
  source  = "../../apps/dashboard"
  project = local.project

  dns_zone             = module.dns_zone_base_domain.zone
  docker_repository    = module.docker_registry.repository
  ssl_policy_name      = module.ssl_policy.policy_name
  certificate_map_name = google_certificate_manager_certificate_map.default.name
  cdn_base_url = "https://storage.googleapis.com/${google_storage_bucket.cdn.name}"

  kube_namespace_name    = module.shared_kubernetes_resources.eave_namespace_name
  shared_config_map_name = module.shared_kubernetes_resources.shared_config_map_name

  LOG_LEVEL = "DEBUG"

  release_date    = "unknown"
  release_version = "latest"

  EAVE_CREDENTIALS = var.INTERNAL_EAVE_CREDENTIALS
}

module "metabase" {
  source  = "../../apps/metabase"
  project = local.project
  metabase_instances = {
    "b579428e" = {
      metabase_instance_id = "b579428e"
      team_id              = "4b885eea03f6488b93b186e2eeff5e13"
    },
    "b1b08034" = {
      metabase_instance_id = "b1b08034"
      team_id              = "f409e437dfa74364ab8fae00e77ce42b"
    },
    "40115f0c" = {
      metabase_instance_id = "40115f0c"
      team_id              = "4d734b7a106c46159bb1013f4caeb463"
    },
  }

  cloudsql_instance_name = module.cloudsql_eave_core.instance.name
  dns_zone               = module.dns_zone_base_domain.zone
  ssl_policy_name        = module.ssl_policy.policy_name
  certificate_map_name   = google_certificate_manager_certificate_map.default.name

  kube_namespace_name          = module.shared_kubernetes_resources.metabase_namespace_name
  MB_SHARED_SECRETS            = var.MB_SHARED_SECRETS
  MB_INSTANCE_SECRETS          = var.MB_INSTANCE_SECRETS
  IAP_OAUTH_CLIENT_CREDENTIALS = var.IAP_OAUTH_CLIENT_CREDENTIALS
}
