# This module creates a low-cost VM that can be accessed through IAP from local workstations.
# The service accounts installed on these VMs are allowed to impersonate another service accounts.
# This is useful for troubleshooting systems that don't have a public IP address, like CloudSQL or Redis.
# The VMs are "Spot" VMs because they're expected to be used sparingly and intermittently.

resource "google_service_account" "bastion_sa" {
  # The service account that will be installed on the VM
  account_id   = var.name
  display_name = "${var.target_service_account_id} bastion agent"
  description  = "Used to impersonate ${var.target_service_account_id} through IAP."
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

resource "google_compute_instance" "bastion" {
  name                    = var.name
  description               = "IAP tunnel for impersonating ${var.target_service_account_id} from local workstations."
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
        --impersonate-service-account ${data.google_service_account.target_service_account.email} \
        --address 0.0.0.0 \
        --port 5432 \
        ${data.google_sql_database_instance.given.connection_name}
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
  network_interface {
    internal_ipv6_prefix_length = 0
    network                     = data.google_compute_network.given.self_link
    # network_ip                  = "10.128.0.14"
    queue_count                 = 0
    stack_type                  = "IPV4_ONLY"
    subnetwork                  = var.subnetwork_self_link
  }
  reservation_affinity {
    type = "ANY_RESERVATION"
  }
  scheduling {
    automatic_restart           = false
    instance_termination_action = "STOP"
    min_node_cpus               = 0
    on_host_maintenance         = "TERMINATE"
    preemptible                 = true
    provisioning_model          = "SPOT"
  }
  service_account {
    email  = google_service_account.bastion_sa.email
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }
  shielded_instance_config {
    enable_integrity_monitoring = false
    enable_secure_boot          = false
    enable_vtpm                 = false
  }
}

resource "google_compute_instance_iam_binding" "bastion_vm_compute_vm_accessor_role_members" {
  # Grant developers access to login to the bastion VM through IAP
  instance_name = google_compute_instance.bastion.name
  role          = data.google_iam_role.compute_vm_accessor_role.id
  members       = var.accessors
}

# https://cloud.google.com/iap/docs/using-tcp-forwarding#create-firewall-rule
resource "google_compute_firewall" "allow_iap_ingress_to_bastion_vm" {
  # Create a firewall rule to allow ingress to the bastion VM from the IAP Tunnel servers
  name          = "allow-iap-ingress-to-${google_service_account.bastion_sa.account_id}"
  description   = "Allow ingress from IAP tunnel to specific ports of ${google_compute_instance.bastion.name}"
  disabled      = false
  direction     = "INGRESS"
  network       = var.network_name
  priority      = 65534
  source_ranges = ["35.235.240.0/20"] // this is the GCP IAP tunnel cidr block

  target_service_accounts = [google_service_account.bastion_sa.id]

  allow {
    ports    = ["5432"] # 5432 is the port on which the cloud-sql-proxy listens.
    protocol = "tcp"
  }
}
