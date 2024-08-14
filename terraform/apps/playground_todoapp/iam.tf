module "service_accounts" {
  # Create the app service account and KSA binding
  source              = "../../modules/gke_app_service_account"
  kube_service_name   = module.kubernetes_service.name
  kube_namespace_name = var.kube_namespace_name
}

module "app_iam_role" {
  # Create a role for this app
  source      = "../../modules/custom_role"
  role_id     = "eave.playgroundTodoApp"
  title       = "Eave Playground Todo App"
  description = "Project permissions needed by the Playground Todo App"
  base_roles = [
    "roles/logging.logWriter",
  ]
}

resource "google_project_iam_binding" "project_app_role_members" {
  # Add the new app role to the app service account
  project = data.google_project.default.project_id
  role    = module.app_iam_role.id
  members = [ data.google_service_account.app_service_account.member ]
}

module "cloudsql_bastion" {
  # Creates the CloudSQL bastion, firewall rule, and IAM bindings
  source = "../../modules/cloudsql_bastion"
  app_service_account_id = module.service_accounts.gsa_account_id
  cloudsql_instance_name = var.cloudsql_instance_name
  network_name = var.network_name
  subnetwork_self_link = var.subnetwork_self_link
  compute_vm_accessor_role_name = var.compute_vm_accessor_role_name
}

resource "google_service_account_iam_binding" "cloudsql_bastion_app_impersonator" {
  # Add impersonators to the app service account
  service_account_id = data.google_service_account.app_service_account.id
  role               = data.google_iam_role.impersonator_role.id
  members             = [
    data.google_service_account.cloudsql_bastion_service_account.member
  ]
}
