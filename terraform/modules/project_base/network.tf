resource "google_compute_network" "primary" {
  lifecycle {
    prevent_destroy = true
  }

  name                                      = "primary"
  auto_create_subnetworks                   = false
  delete_default_routes_on_create           = false
  description                               = "Eave primary VPC network"
  enable_ula_internal_ipv6                  = false
  internal_ipv6_range                       = null
  mtu                                       = 0
  network_firewall_policy_enforcement_order = "AFTER_CLASSIC_FIREWALL"
  routing_mode                              = "REGIONAL"
}

resource "google_compute_subnetwork" "primary" {
  lifecycle {
    prevent_destroy = true
  }

  name                     = "primary"
  region                   = var.subnet_region
  ip_cidr_range            = "10.128.0.0/20"
  network                  = google_compute_network.primary.id
  private_ip_google_access = true

  log_config {
    aggregation_interval = "INTERVAL_10_MIN"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }

  # secondary_ip_range {
  #   range_name    = "tf-test-secondary-range-update1"
  #   ip_cidr_range = "10.56.128.0/17"
  # }
}

resource "google_dns_policy" "primary" {
  lifecycle {
    prevent_destroy = true
  }

  name                      = "primary"
  enable_inbound_forwarding = true
  enable_logging            = true

  networks {
    network_url = google_compute_network.primary.id
  }
}

# Create an internal IP address for service networking
resource "google_compute_global_address" "private_ip_range" {
  lifecycle {
    prevent_destroy = true
  }

  name          = "google-managed-services-${google_compute_network.primary.name}"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.primary.id
}

# Create a private connection
resource "google_service_networking_connection" "default" {
  lifecycle {
    prevent_destroy = true
  }

  network                 = google_compute_network.primary.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_range.name]
}