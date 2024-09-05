module "cloudsql_bastion" {
  source = "../../modules/cloudsql_bastion_vm"
  name = "${local.app_name}-bastion"
  target_service_account_id = module.service_accounts.gsa_account_id
  cloudsql_instance_name = var.cloudsql_instance_name
  network_name = var.network_name
  subnetwork_self_link = var.subnetwork_self_link
  compute_vm_accessor_role_name = var.compute_vm_accessor_role_name
  accessors = var.bastion_accessors
}
