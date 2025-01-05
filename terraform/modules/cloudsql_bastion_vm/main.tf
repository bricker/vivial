# This module creates a low-cost VM that can be accessed through IAP from local workstations.
# The service accounts installed on these VMs are allowed to impersonate another service accounts.
# This is useful for troubleshooting systems that don't have a public IP address, like CloudSQL or Redis.
# The VMs are "Spot" VMs because they're expected to be used sparingly and intermittently.

resource "google_service_account" "bastion_sa" {
  # The service account that will be installed on the VM
  account_id   = var.name
  display_name = "${var.target_service_account.account_id} bastion agent"
  description  = "Used to impersonate ${var.target_service_account.account_id} through IAP."
}

resource "google_compute_instance" "bastion" {
  name                      = var.name
  description               = "IAP tunnel for impersonating ${var.target_service_account.account_id} from local workstations."
  machine_type              = "n2d-standard-2" # Required for confidential compute
  allow_stopping_for_update = true
  can_ip_forward            = false
  deletion_protection       = false
  enable_display            = false
  min_cpu_platform          = "AMD Milan"

  confidential_instance_config {
    enable_confidential_compute = true
    confidential_instance_type  = "SEV"
  }

  metadata = {
    block-project-ssh-keys = "true"
    enable-oslogin         = "true"
    enable-oslogin-2fa     = "true"
    startup-script         = <<-EOT
      sudo apt-get update
      sudo apt install -y \
        wget \
        postgresql-client

      if ! test -f cloud-sql-proxy; then
        wget https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.2/cloud-sql-proxy.linux.amd64 -O cloud-sql-proxy
      fi

      chmod +x cloud-sql-proxy
      ./cloud-sql-proxy \
        --private-ip \
        --auto-iam-authn \
        --impersonate-service-account ${var.target_service_account.email} \
        --address 0.0.0.0 \
        --port 5432 \
        ${var.google_sql_database_instance.connection_name}
    EOT
  }

  boot_disk {
    auto_delete = true
    mode        = "READ_WRITE"
    initialize_params {
      image = "projects/ubuntu-os-cloud/global/images/ubuntu-2004-focal-v20240830" # confidential compute compatible image
      size  = 10
      type  = "pd-standard"
    }
  }

  network_interface {
    nic_type    = "GVNIC" # Required for confidential compute
    queue_count = 0
    stack_type  = "IPV4_ONLY"
    network     = var.google_compute_network.name
    subnetwork  = var.google_compute_subnetwork.name
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
    enable_integrity_monitoring = true
    enable_secure_boot          = true
    enable_vtpm                 = true
  }
}
