# https://cloud.google.com/iap/docs/using-tcp-forwarding#create-firewall-rule
resource "google_compute_firewall" "iap_ssh_tunnel" {
  name                    = "allow-ssh-ingress-from-iap"
  description             = "Allow SSH ingress from IAP tunnel"
  disabled = false
  direction               = "INGRESS"
  network                 = module.project_base.network_name
  priority                = 65534
  source_ranges           = ["35.235.240.0/20"] // this is the GCP IAP tunnel cidr block

  allow {
    ports    = ["22", "5432"]
    protocol = "tcp"
  }
}

# # https://cloud.google.com/iap/docs/using-tcp-forwarding#grant-permission
# roles/iap.tunnelResourceAccessor
# resource "" "iap_tcp_forwarding" {

# }