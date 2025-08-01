resource "google_compute_ssl_policy" "default" {
  lifecycle {
    prevent_destroy = true
  }

  name            = "default-ssl-policy"
  profile         = "MODERN"  # Mandatory for compliance
  min_tls_version = "TLS_1_2" # Mandatory for compliance
}
