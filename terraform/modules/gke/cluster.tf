// https://cloud.google.com/kubernetes-engine/docs/quickstarts/create-cluster-using-terraform

resource "google_container_cluster" "default" {
  # lifecycle {
  #   prevent_destroy = true
  # }

  name             = var.cluster_name
  location         = var.location
  network          = var.google_compute_network.name
  subnetwork       = var.google_compute_subnetwork.name
  enable_autopilot = true

  # Set `deletion_protection` to `true` will ensure that one cannot
  # accidentally delete this instance by use of Terraform.
  deletion_protection = false

  cluster_autoscaling {
    auto_provisioning_defaults {
      service_account = var.use_default_service_account ? null : google_service_account.gke_node.email
    }
  }

  node_config {
    service_account = var.use_default_service_account ? null : google_service_account.gke_node.email

    gvnic {
      enabled = true
    }

    reservation_affinity {
        consume_reservation_type = "NO_RESERVATION"
    }
  }

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
