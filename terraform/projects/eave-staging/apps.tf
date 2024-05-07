module "core_api_app" {
  source = "../../apps/core_api"
  project = local.project

  cloudsql_instance_name = module.cloudsql_eave_core.instance.name
  dns_zone = module.dns_zone_base_domain.zone
  docker_repository = module.docker_registry.repository

  kube_namespace_name = module.shared_kubernetes_resources.eave_namespace_name
  shared_config_map_name = module.shared_kubernetes_resources.shared_config_map_name

  LOG_LEVEL = "DEBUG"

  release_date = "unknown"
  release_version = "latest"
}

module "playground_todoapp" {
  source = "../../apps/playground_todoapp"
  project = local.project

  cloudsql_instance_name = module.cloudsql_eave_core.instance.name
  dns_zone = module.dns_zone_base_domain.zone
  docker_repository = module.docker_registry.repository

  kube_namespace_name = module.shared_kubernetes_resources.eave_namespace_name
  shared_config_map_name = module.shared_kubernetes_resources.shared_config_map_name

  LOG_LEVEL = "DEBUG"

  release_date = "unknown"
  release_version = "latest"
}

module "dashboard_app" {
  source = "../../apps/dashboard"
  project = local.project

  dns_zone = module.dns_zone_base_domain.zone
  docker_repository = module.docker_registry.repository

  kube_namespace_name = module.shared_kubernetes_resources.eave_namespace_name
  shared_config_map_name = module.shared_kubernetes_resources.shared_config_map_name

  LOG_LEVEL = "DEBUG"

  release_date = "unknown"
  release_version = "latest"
}

module "metabase" {
  source = "../../apps/metabase"
  project = local.project
  metabase_instances = [
    "dev"
  ]

  kube_namespace_name = module.shared_kubernetes_resources.metabase_namespace_name
  cloudsql_instance_name = module.cloudsql_eave_core.instance.name
  MB_SHARED_SECRETS = var.MB_SHARED_SECRETS
  MB_INSTANCE_SECRETS = var.MB_INSTANCE_SECRETS
}
