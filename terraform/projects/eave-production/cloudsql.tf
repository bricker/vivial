module "cloudsql_eave_core" {
  source              = "../../modules/cloudsql_instance"
  instance_name       = "eave-pg-core"
  network_name        = module.project_base.network_name
  environment         = local.environment
  global_address_name = module.project_base.private_ip_range_name
}

module "cloudsql_iam" {
  source = "../../modules/cloudsql_iam"
  cloudsql_instance_name = module.cloudsql_eave_core.cloudsql_instance_name
  cloudsql_user_role_id = module.project_base.cloudsql_user_role_id
  members = [
    data.google_service_account.app_service_accounts[module.core_api_app.service_account_id].member,
    data.google_service_account.app_service_accounts[module.playground_todoapp.service_account_id].member,
  ]
}
