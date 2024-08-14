module "cloudsql_bastion_core_api" {
  source = "../../modules/cloudsql_bastion"
  app_service_account_id = module.core_api_app.service_account_id
  cloudsql_instance_name = module.cloudsql_eave_core.cloudsql_instance_name
  network_name = module.project_base.network_name
  subnetwork_self_link = module.project_base.subnetwork_self_link
}