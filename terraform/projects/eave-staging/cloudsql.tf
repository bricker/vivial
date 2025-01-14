module "cloudsql_eave_core" {
  source                 = "../../modules/cloudsql_instance"
  instance_name          = "eave-pg-core-stg"
  google_compute_network = module.project_base.google_compute_network
  global_address_name    = module.project_base.private_ip_range_name
  preset                 = "NONPROD"
  enable_backups         = false
  disk_size_gb           = 10

  cloudsql_user_role_members = [
    module.core_api_app.service_account.member,
  ]
}
