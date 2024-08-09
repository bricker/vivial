# resource "google_compute_instance" "cloudsql_bastion_core_api" {
#   allow_stopping_for_update = null
#   can_ip_forward            = false
#   deletion_protection       = false
#   description               = null
#   desired_status            = null
#   enable_display            = false
#   guest_accelerator         = []
#   hostname                  = null
#   labels                    = {}
#   machine_type              = "e2-micro"
#   metadata = {
#     block-project-ssh-keys = "true"
#     enable-oslogin-2fa     = "true"
#     startup-script         = "sudo apt-get update && sudo apt-get install wget && wget https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.2/cloud-sql-proxy.linux.amd64 -O cloud-sql-proxy && chmod +x cloud-sql-proxy && ./cloud-sql-proxy --private-ip eave-staging:us-central1:eave-pg-core"
#   }
#   metadata_startup_script = null
#   min_cpu_platform        = null
#   name                    = "cloudsql-bastion-core-api"
#   resource_policies       = []
#   tags                    = []
#   boot_disk {
#     auto_delete             = true
#     device_name             = "cloudsql-bastion-core-api"
#     disk_encryption_key_raw = null # sensitive
#     kms_key_self_link       = null
#     mode                    = "READ_WRITE"
#     source                  = "https://www.googleapis.com/compute/v1/projects/eave-staging/zones/us-central1-a/disks/cloudsql-bastion-core-api"
#     initialize_params {
#       enable_confidential_compute = false
#       image                       = "https://www.googleapis.com/compute/v1/projects/debian-cloud/global/images/debian-12-bookworm-v20240709"
#       labels                      = {}
#       provisioned_iops            = 0
#       provisioned_throughput      = 0
#       resource_manager_tags       = {}
#       size                        = 10
#       type                        = "pd-balanced"
#     }
#   }
#   confidential_instance_config {
#     enable_confidential_compute = false
#   }
#   network_interface {
#     internal_ipv6_prefix_length = 0
#     ipv6_address                = null
#     network                     = "https://www.googleapis.com/compute/v1/projects/eave-staging/global/networks/primary"
#     network_ip                  = "10.128.0.14"
#     nic_type                    = null
#     queue_count                 = 0
#     stack_type                  = "IPV4_ONLY"
#     subnetwork                  = "https://www.googleapis.com/compute/v1/projects/eave-staging/regions/us-central1/subnetworks/primary"
#   }
#   reservation_affinity {
#     type = "ANY_RESERVATION"
#   }
#   scheduling {
#     automatic_restart           = false
#     instance_termination_action = "STOP"
#     min_node_cpus               = 0
#     on_host_maintenance         = "TERMINATE"
#     preemptible                 = true
#     provisioning_model          = "SPOT"
#   }
#   service_account {
#     email  = "gsa-app-core-api@eave-staging.iam.gserviceaccount.com"
#     scopes = ["https://www.googleapis.com/auth/cloud-platform"]
#   }
#   shielded_instance_config {
#     enable_integrity_monitoring = false
#     enable_secure_boot          = false
#     enable_vtpm                 = false
#   }
# }
