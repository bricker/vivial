output "default_network" {
  value = google_compute_network.default
}

resource "google_compute_network" "default" {
  auto_create_subnetworks                   = true
  delete_default_routes_on_create           = false
  description                               = "Default network for the project"
  enable_ula_internal_ipv6                  = false
  internal_ipv6_range                       = null
  mtu                                       = 0
  name                                      = "default"
  network_firewall_policy_enforcement_order = "AFTER_CLASSIC_FIREWALL"
  project                                   = var.project_id
  routing_mode                              = "REGIONAL"
}

# resource "google_compute_subnetwork" "default" {
#   description                = null
#   external_ipv6_prefix       = null
#   ip_cidr_range              = "10.128.0.0/20"
#   ipv6_access_type           = null
#   name                       = "default"
#   network                    = "https://www.googleapis.com/compute/v1/projects/eave-staging/global/networks/default"
#   private_ip_google_access   = true
#   private_ipv6_google_access = "DISABLE_GOOGLE_ACCESS"
#   project                    = "eave-staging"
#   purpose                    = "PRIVATE"
#   region                     = "us-central1"
#   role                       = null
#   secondary_ip_range = [{
#     ip_cidr_range = "10.79.128.0/17"
#     range_name    = "gke-eave-gke-cluster-pods-46b5475c"
#   }]
#   stack_type = "IPV4_ONLY"
# }
