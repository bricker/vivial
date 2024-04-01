variable "network_id" {
  type = string
}

variable "subnetwork_id" {
  type = string
}

variable "authorized_networks" {
  type = map(object({
    cidr_block = string
    display_name = string
  }))

  default = {}
}

resource "google_container_cluster" "eave_gke_cluster" {
  name                        = "eave-gke-cluster"
  enable_autopilot            = true
  location                    = var.region
  project                     = var.project_id
  network                     = var.network_id
  subnetwork                  = var.subnetwork_id
  deletion_protection         = true
  # allow_net_admin             = null
  # cluster_ipv4_cidr           = "10.79.128.0/17"
  # datapath_provider           = "ADVANCED_DATAPATH"
  # default_max_pods_per_node   = 110
  # description                 = null
  # enable_intranode_visibility = true
  # enable_kubernetes_alpha     = false
  # enable_l4_ilb_subsetting    = false
  # enable_legacy_abac          = false
  # enable_shielded_nodes       = true
  # enable_tpu                  = false
  # initial_node_count          = 0
  # logging_service             = "logging.googleapis.com/kubernetes"
  # min_master_version          = null
  # monitoring_service          = "monitoring.googleapis.com/kubernetes"
  # networking_mode             = "VPC_NATIVE"
  # node_locations              = ["us-central1-a", "us-central1-b", "us-central1-c", "us-central1-f"]
  # node_version                = "1.27.8-gke.1067004"
  # private_ipv6_google_access  = null
  # remove_default_node_pool    = null
  # resource_labels             = {}
  # addons_config {
  #   dns_cache_config {
  #     enabled = true
  #   }
  #   gce_persistent_disk_csi_driver_config {
  #     enabled = true
  #   }
  #   gcp_filestore_csi_driver_config {
  #     enabled = true
  #   }
  #   gcs_fuse_csi_driver_config {
  #     enabled = true
  #   }
  #   horizontal_pod_autoscaling {
  #     disabled = false
  #   }
  #   http_load_balancing {
  #     disabled = false
  #   }
  #   network_policy_config {
  #     disabled = true
  #   }
  # }
  # authenticator_groups_config {
  #   security_group = ""
  # }
  # binary_authorization {
  #   evaluation_mode = "DISABLED"
  # }
  # cluster_autoscaling {
  #   autoscaling_profile = "OPTIMIZE_UTILIZATION"
  #   enabled             = true
  #   auto_provisioning_defaults {
  #     boot_disk_kms_key = null
  #     disk_size         = 0
  #     disk_type         = null
  #     image_type        = "COS_CONTAINERD"
  #     min_cpu_platform  = null
  #     oauth_scopes      = ["https://www.googleapis.com/auth/devstorage.read_only", "https://www.googleapis.com/auth/logging.write", "https://www.googleapis.com/auth/monitoring", "https://www.googleapis.com/auth/service.management.readonly", "https://www.googleapis.com/auth/servicecontrol", "https://www.googleapis.com/auth/trace.append"]
  #     service_account   = "default"
  #     management {
  #       auto_repair  = true
  #       auto_upgrade = true
  #     }
  #     upgrade_settings {
  #       max_surge       = 1
  #       max_unavailable = 0
  #       strategy        = "SURGE"
  #     }
  #   }
  #   resource_limits {
  #     maximum       = 1000000000
  #     minimum       = 0
  #     resource_type = "cpu"
  #   }
  #   resource_limits {
  #     maximum       = 1000000000
  #     minimum       = 0
  #     resource_type = "memory"
  #   }
  #   resource_limits {
  #     maximum       = 1000000000
  #     minimum       = 0
  #     resource_type = "nvidia-tesla-t4"
  #   }
  #   resource_limits {
  #     maximum       = 1000000000
  #     minimum       = 0
  #     resource_type = "nvidia-tesla-a100"
  #   }
  # }
  # database_encryption {
  #   key_name = null
  #   state    = "DECRYPTED"
  # }
  # default_snat_status {
  #   disabled = false
  # }
  # dns_config {
  #   cluster_dns        = "CLOUD_DNS"
  #   cluster_dns_domain = "cluster.local"
  #   cluster_dns_scope  = "CLUSTER_SCOPE"
  # }
  # gateway_api_config {
  #   channel = "CHANNEL_STANDARD"
  # }
  # ip_allocation_policy {
  #   cluster_ipv4_cidr_block       = "10.79.128.0/17"
  #   cluster_secondary_range_name  = "gke-eave-gke-cluster-pods-46b5475c"
  #   services_ipv4_cidr_block      = "34.118.224.0/20"
  #   services_secondary_range_name = null
  #   stack_type                    = "IPV4"
  #   pod_cidr_overprovision_config {
  #     disabled = false
  #   }
  # }
  # logging_config {
  #   enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]
  # }
  # master_auth {
  #   client_certificate_config {
  #     issue_client_certificate = false
  #   }
  # }
  master_authorized_networks_config {
    gcp_public_cidrs_access_enabled = false

    dynamic "cidr_blocks" {
      for_each = var.authorized_networks
      content {
        cidr_block   = each.value.cidr_block
        display_name = each.value.display_name
      }
    }
  }

  private_cluster_config {
    enable_private_endpoint     = false
    enable_private_nodes        = true
    # master_ipv4_cidr_block      = "172.16.49.0/28"
    # private_endpoint_subnetwork = null
    master_global_access_config {
      enabled = false
    }
  }
  # release_channel {
  #   channel = "REGULAR"
  # }
  # security_posture_config {
  #   mode               = "BASIC"
  #   vulnerability_mode = "VULNERABILITY_BASIC"
  # }
  service_external_ips_config {
    enabled = false
  }
  # vertical_pod_autoscaling {
  #   enabled = true
  # }
  # workload_identity_config {
  #   workload_pool = "${var.project_id}.svc.id.goog"
  # }
}
