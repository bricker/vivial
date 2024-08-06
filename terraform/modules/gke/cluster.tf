// https://cloud.google.com/kubernetes-engine/docs/quickstarts/create-cluster-using-terraform

resource "google_container_cluster" "default" {
  name             = var.cluster_name
  location         = var.location
  network          = data.google_compute_network.given.self_link
  subnetwork       = var.subnetwork_self_link
  enable_autopilot = true

  # Set `deletion_protection` to `true` will ensure that one cannot
  # accidentally delete this instance by use of Terraform.
  deletion_protection = false

  master_authorized_networks_config {
    gcp_public_cidrs_access_enabled = false

    dynamic "cidr_blocks" {
      for_each = var.authorized_networks
      content {
        cidr_block   = cidr_blocks.value.cidr_block
        display_name = cidr_blocks.value.display_name
      }
    }
  }

  private_cluster_config {
    enable_private_endpoint = false
    enable_private_nodes    = true
    master_global_access_config {
      enabled = false
    }
  }

  service_external_ips_config {
    enabled = false
  }
}
