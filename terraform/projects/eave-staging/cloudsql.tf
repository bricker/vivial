module "cloudsql_eave_core" {
  source              = "../../modules/cloudsql_instance"
  instance_name       = "eave-pg-core"
  network_name        = module.project_base.network_name
  environment         = local.environment
  global_address_name = module.project_base.private_ip_range_name

  cloudsql_user_role_name = module.project_base.cloudsql_user_role_name
  cloudsql_user_role_members = [
    data.google_service_account.app_service_accounts[module.core_api_app.service_account_id].member,
  ]

}

moved {
  from = module.cloudsql_iam
  to   = module.cloudsql_eave_core.module.cloudsql_iam
}
