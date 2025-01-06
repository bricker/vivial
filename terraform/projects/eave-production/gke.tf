module "gke_primary" {
  source                      = "../../modules/gke"
  cluster_name                = "primary"
  location                    = local.default_region # Autopilot clusters must be regional
  authorized_networks         = local.authorized_networks
  google_compute_network      = module.project_base.google_compute_network
  google_compute_subnetwork   = module.project_base.google_compute_subnetwork
  docker_repository_ref       = module.project_base.docker_repository_ref
  use_default_service_account = true
}
