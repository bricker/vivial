variable "project_id" {
  type = string
}

variable "region" {
  type = string
}


# https://www.hashicorp.com/blog/terraform-adds-support-for-gke-autopilot
# resource "google_container_cluster" "primary" {
#   name     = "${var.project_id}-gke"
#   location = var.region

#   network    = google_compute_network.vpc.name
#   subnetwork = google_compute_subnetwork.subnet.name

# # Enabling Autopilot for this cluster
#   enable_autopilot = true
# }

resource "google_container_cluster" "eave_services" {
  name                = "eave-services"
  location            = var.region
  network             = "projects/${var.project_id}/global/networks/default"
  subnetwork          = "projects/${var.project_id}/regions/${var.region}/subnetworks/default"
  networking_mode     = "VPC_NATIVE"
  enable_autopilot    = true
  deletion_protection = true

  ip_allocation_policy {
  }

  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = "157.22.33.161/32"
      display_name = "Bryan's Home Wifi"
    }
    cidr_blocks {
      cidr_block   = "76.146.71.81/32"
      display_name = "Liam's Home Wifi"
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
  timeouts {
    create = null
    delete = null
    read   = null
    update = null
  }
}
