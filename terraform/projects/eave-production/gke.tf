# module "gke_primary" {
#   source              = "../../modules/gke"
#   cluster_name = "primary"
#   location            = local.default_region # Autopilot clusters must be regional
#   authorized_networks = local.authorized_networks
#   network_name = module.project_base.network_name
#   subnetwork_self_link = module.project_base.subnetwork_self_link
#   root_domain = local.root_domain
# }
