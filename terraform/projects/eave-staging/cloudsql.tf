module "cloudsql_eave_core" {
  source              = "../../modules/cloudsql_instance"
  instance_name       = "eave-pg-core"
  network_name        = module.project_base.network_name
  environment         = local.environment
  global_address_name = module.project_base.private_ip_range_name
}
