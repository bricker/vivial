# The service account that will be installed on the VM
resource "google_service_account" "cloudsql_bastion_sa" {
  account_id   = "cloudsql-bastion"
  display_name = "CloudSQL bastion agent"
  description  = "The service account for the CloudSQL bastion VM"
}

# resource "google_compute_disk" "cloudsql_bastion" {
#   name  = "cloudsql-bastion"
#   type  = "pd-ssd"
#   zone  = "us-central1-a"
#   image = "debian-11-bullseye-v20220719"
#   labels = {
#     environment = "dev"
#   }
#   physical_block_size_bytes = 4096
# }

resource "google_compute_instance" "cloudsql_bastion" {
  name                    = "cloudsql-bastion-core-api"
  description               = "IAP tunnel for connecting to CloudSQL from local workstations"
  can_ip_forward            = false
  deletion_protection       = false
  desired_status            = "RUNNING"
  enable_display            = false
  machine_type              = "e2-micro"
  metadata = {
    block-project-ssh-keys = "true"
    enable-oslogin-2fa     = "true"
    startup-script         = <<-EOT
      set -e
      sudo apt-get update
      sudo apt install postgresql-client
      sudo apt-get install wget
      wget https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.2/cloud-sql-proxy.linux.amd64 -O cloud-sql-proxy
      chmod +x cloud-sql-proxy
      ./cloud-sql-proxy \
        --private-ip \
        --auto-iam-authn \
        --impersonate-service-account ${data.google_service_account.app_service_accounts[module.core_api_app.service_account_id].email} \
        --address 0.0.0.0 \
        --port 5432 \
        --health-check \
        --http-address localhost \
        --http-port 9090 \
        ${data.google_sql_database_instance.eave_pg_core.connection_name}
    EOT
  }
  boot_disk {
    auto_delete             = true
    mode                    = "READ_WRITE"
    initialize_params {
      enable_confidential_compute = false
      image                       = "https://www.googleapis.com/compute/v1/projects/debian-cloud/global/images/debian-12-bookworm-v20240709"
      provisioned_iops            = 0
      provisioned_throughput      = 0
      size                        = 10
      type                        = "pd-balanced"
    }
  }
  confidential_instance_config {
    enable_confidential_compute = false
  }
  network_interface {
    internal_ipv6_prefix_length = 0
    network                     = data.google_compute_network.primary.self_link
    # network_ip                  = "10.128.0.14"
    queue_count                 = 0
    stack_type                  = "IPV4_ONLY"
    subnetwork                  = data.google_compute_subnetwork.primary.self_link
  }
  reservation_affinity {
    type = "ANY_RESERVATION"
  }
  scheduling {
    automatic_restart           = true
    instance_termination_action = "STOP"
    min_node_cpus               = 0
    on_host_maintenance         = "TERMINATE"
    preemptible                 = true
    provisioning_model          = "SPOT"
  }
  service_account {
    email  = google_service_account.cloudsql_bastion_sa.email
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }
  shielded_instance_config {
    enable_integrity_monitoring = false
    enable_secure_boot          = false
    enable_vtpm                 = false
  }
}

module "cloudsql_bastion_user_role" {
  # Create a role that can login to the bastion VM
  source  = "../../modules/custom_role"
  role_id = "eave.cloudsqlBastionUser"
  title   = "Access to use the cloudsql bastion service account"
  base_roles = [
    "roles/iam.serviceAccountUser",
    "roles/compute.osLogin",
  ]
}

resource "google_compute_instance_iam_binding" "cloudsql_bastion_sa_cloudsql_bastion_user_role_members" {
  # Grant developers access to login to the bastion VM through IAP
  instance_name = google_compute_instance.cloudsql_bastion.name
  role          = module.cloudsql_bastion_user_role.id
  members       = [
    "group:developer@eave.fyi",
  ]
}

# https://cloud.google.com/iap/docs/using-tcp-forwarding#create-firewall-rule
resource "google_compute_firewall" "allow_iap_ingress_to_cloudsql_bastion" {
  # Create a firewall rule to allow ingress to the bastion VM from the IAP Tunnel servers
  # name          = "allow-iap-ingress-to-cloudsql-bastion"
  name          = "allow-ssh-ingress-from-iap"
  description   = "Allow ingress from IAP tunnel to specific ports of the CloudSQL Bastion instance"
  disabled      = false
  direction     = "INGRESS"
  network       = module.project_base.network_name
  priority      = 65534
  source_ranges = ["35.235.240.0/20"] // this is the GCP IAP tunnel cidr block

  target_service_accounts = [google_service_account.cloudsql_bastion_sa.id]

  allow {
    ports    = ["22", "5432"] # 5432 is the port on which the cloud-sql-proxy listens. 22 is ssh for troubleshooting.
    protocol = "tcp"
  }
}
