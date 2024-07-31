# import {
#   id = "projects/eave-staging/global/networks/default"
#   to = google_compute_network.default
# }

resource "google_compute_network" "default" {
  name                                      = "default"
  auto_create_subnetworks                   = true
  delete_default_routes_on_create           = false
  description                               = "Default network for the project"
  enable_ula_internal_ipv6                  = false
  internal_ipv6_range                       = null
  mtu                                       = 0
  network_firewall_policy_enforcement_order = "AFTER_CLASSIC_FIREWALL"
  routing_mode                              = "REGIONAL"
}

resource "google_compute_network" "primary" {
  name                                      = "primary"
  auto_create_subnetworks                   = true
  delete_default_routes_on_create           = false
  description                               = "Eave primary VPC network"
  enable_ula_internal_ipv6                  = false
  internal_ipv6_range                       = null
  mtu                                       = 0
  network_firewall_policy_enforcement_order = "AFTER_CLASSIC_FIREWALL"
  routing_mode                              = "REGIONAL"
}
