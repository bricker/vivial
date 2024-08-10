# The service account that will be installed on the VM
resource "google_service_account" "cloudsql_bastion_sa" {
  account_id   = "cloudsql-bastion"
  display_name = "CloudSQL bastion agent"
  description = "The service account for the CloudSQL bastion VM"
}

module "cloudsql_bastion_user_sa" {
  source  = "../../modules/custom_role"
  role_id = "eave.cloudsqlBastionUser"
  title   = "Access to the CloudSQL Bastion service account for Eave developers"
  base_roles = [
    "roles/iam.serviceAccountUser"
  ]
  members = [
    "group:developers@eave.fyi",
  ]
}

# resource "google_compute_instance" "cloudsql_bastion_core_api" {
#   name                    = "cloudsql-bastion-core-api"
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
#     startup-script         = "sudo apt-get update && sudo apt install postgresql-client && sudo apt-get install wget && wget https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.2/cloud-sql-proxy.linux.amd64 -O cloud-sql-proxy && chmod +x cloud-sql-proxy && ./cloud-sql-proxy --private-ip --auto-iam-authn --impersonate-service-account gsa-app-core-api@eave-staging.iam.gserviceaccount.com --address 0.0.0.0 --port 5432 --health-check --http-address localhost --http-port 9090 eave-staging:us-central1:eave-pg-core"
#   }
#   metadata_startup_script = null
#   min_cpu_platform        = null
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
#     network                     = data.google_compute_network.primary.self_link
#     # network_ip                  = "10.128.0.14"
#     nic_type                    = null
#     queue_count                 = 0
#     stack_type                  = "IPV4_ONLY"
#     subnetwork                  = data.google_compute_subnetwork.primary.self_link
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
#     email  = google_service_account.cloudsql_bastion_sa.email
#     scopes = ["https://www.googleapis.com/auth/cloud-platform"]
#   }
#   shielded_instance_config {
#     enable_integrity_monitoring = false
#     enable_secure_boot          = false
#     enable_vtpm                 = false
#   }
# }

resource "google_compute_instance_iam_binding" "cloudsql_bastion_iam_bindign" {
  instance_name = "value"
  role = "value"
  members = [ "value" ]
}

# https://cloud.google.com/iap/docs/using-tcp-forwarding#create-firewall-rule
resource "google_compute_firewall" "allow_iap_ingress_to_cloudsql_bastion" {
  name                    = "allow-iap-ingress-to-cloudsql-bastion"
  description             = "Allow ingress from IAP tunnel to specific ports of the CloudSQL Bastion instance"
  disabled = false
  direction               = "INGRESS"
  network                 = module.project_base.network_name
  priority                = 65534
  source_ranges           = ["35.235.240.0/20"] // this is the GCP IAP tunnel cidr block

  target_service_accounts = [ google_service_account.cloudsql_bastion_sa.id ]

  allow {
    ports    = ["22", "5432"] # 5432 is the port on which the cloud-sql-proxy listens. 22 is ssh for troubleshooting.
    protocol = "tcp"
  }
}

# # https://cloud.google.com/iap/docs/using-tcp-forwarding#grant-permission
# roles/iap.tunnelResourceAccessor
# roles/iam.serviceAccountUser
# roles/compute.osLogin
resource "" "iap_tcp_forwarding" {

}

# TODO: Grant osLogin role to users on instance
# https://cloud.google.com/compute/docs/oslogin/set-up-oslogin#configure_users