# https://cloud.google.com/iap/docs/using-tcp-forwarding#create-firewall-rule
resource "google_compute_firewall" "allow_iap_ingress_to_bastion_vm" {
  # Create a firewall rule to allow ingress to the bastion VM from the IAP Tunnel servers
  name          = "allow-iap-ingress-to-${google_service_account.bastion_sa.account_id}"
  description   = "Allow ingress from IAP tunnel to specific ports of ${google_compute_instance.bastion.name}"
  disabled      = false
  direction     = "INGRESS"
  network       = var.google_compute_network.name
  priority      = 65534
  source_ranges = ["35.235.240.0/20"] // this is the GCP IAP tunnel cidr block

  target_service_accounts = [google_service_account.bastion_sa.email]

  allow {
    ports    = ["5432"] # 5432 is the port on which the cloud-sql-proxy listens.
    protocol = "tcp"
  }
}
