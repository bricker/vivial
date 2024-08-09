# resource "google_compute_firewall" "default_allow_ssh" {
#   name                    = "allow-ssh-from-authorized-networks"
#   description             = "Allow SSH from authorized networks"
#   disabled = false
#   direction               = "INGRESS"
#   network                 = module.project_base.network_name
#   priority                = 65534
#   source_ranges           = [for key, network in local.authorized_networks: network.cidr_block]

#   allow {
#     ports    = ["22"]
#     protocol = "tcp"
#   }
# }

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
    ports    = ["22"]
    protocol = "tcp"
  }
}

# # https://cloud.google.com/iap/docs/using-tcp-forwarding#grant-permission
# resource "" "iap_tcp_forwarding" {

# }