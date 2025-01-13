module "bastion" {
  source                         = "../../modules/cloudsql_bastion_vm"
  name                           = "${local.app_name}-bastion"
  target_service_account         = module.service_accounts.google_service_account
  google_sql_database_instance   = var.google_sql_database_instance
  google_compute_network         = var.google_compute_network
  google_compute_subnetwork      = var.google_compute_subnetwork
  compute_oslogin_role_name      = var.compute_oslogin_role_name
  service_account_user_role_name = var.service_account_user_role_name
  accessors                      = var.bastion_accessors
}
