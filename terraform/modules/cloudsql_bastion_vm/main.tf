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

resource "google_compute_instance" "bastion" {
  name                = var.name
  description         = "IAP tunnel for impersonating ${var.target_service_account_id} from local workstations."
  can_ip_forward      = false
  deletion_protection = false
  enable_display      = false
  machine_type        = "e2-micro"
  allow_stopping_for_update = true
  metadata = {
    block-project-ssh-keys = "true"
    enable-oslogin-2fa     = "true"
    startup-script         = <<-EOT
      set -e
      sudo apt-get update

      sudo apt install -y postgresql-client
      sudo apt install -y wget
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
    auto_delete = true
    mode        = "READ_WRITE"
    initialize_params {
      enable_confidential_compute = false
      image                       = "https://www.googleapis.com/compute/v1/projects/debian-cloud/global/images/debian-12-bookworm-v20240709"
      provisioned_iops            = 0
      provisioned_throughput      = 0
      size                        = 10
      type                        = "pd-standard"
    }
  }
  network_interface {
    internal_ipv6_prefix_length = 0
    network                     = data.google_compute_network.given.self_link
    subnetwork  = var.subnetwork_self_link
    queue_count = 0
    stack_type  = "IPV4_ONLY"
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
    max_run_duration {
      seconds = 28800 # 8 hours
    }
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
