variable "location" {
  type = string
  description = "Specify either a region or a zone. Region spreads the cluster out over all zones in the region. Zone deploys the cluster into just one zone. Zone is better for lower environments."
}

variable "authorized_networks" {
  type = map(object({
    cidr_block   = string
    display_name = string
  }))

  default = {}
}

resource "google_container_cluster" "default" {
  name     = "eave-cluster"
  location = var.location

  enable_autopilot = true

  # Set `deletion_protection` to `true` will ensure that one cannot
  # accidentally delete this instance by use of Terraform.
  deletion_protection = true

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

output "cluster" {
  value = google_container_cluster.default
}