# import {
#   id = "projects/eave-staging/global/firewalls/default-allow-ssh"
#   to = google_compute_firewall.default_allow_ssh
# }

resource "google_compute_firewall" "default_allow_ssh" {
  # Must be DISABLED for SOC-2 compliance
  disabled                = true

  description             = "Allow SSH from anywhere"
  destination_ranges      = []
  direction               = "INGRESS"
  name                    = "default-allow-ssh"
  network                 = "https://www.googleapis.com/compute/v1/projects/eave-staging/global/networks/default"
  priority                = 65534
  source_ranges           = ["0.0.0.0/0"]
  source_service_accounts = []
  source_tags             = []
  target_service_accounts = []
  target_tags             = []
  allow {
    ports    = ["22"]
    protocol = "tcp"
  }
}

resource "google_compute_firewall" "default_allow_rdp" {
  # Must be DISABLED for SOC-2 compliance
  disabled                = true

  description             = "Allow RDP from anywhere"
  destination_ranges      = []
  direction               = "INGRESS"
  name                    = "default-allow-rdp"
  network                 = "https://www.googleapis.com/compute/v1/projects/eave-staging/global/networks/default"
  priority                = 65534
  source_ranges           = ["0.0.0.0/0"]
  source_service_accounts = []
  source_tags             = []
  target_service_accounts = []
  target_tags             = []
  allow {
    ports    = ["3389"]
    protocol = "tcp"
  }
}
