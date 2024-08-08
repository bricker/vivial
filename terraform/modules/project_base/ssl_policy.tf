resource "google_compute_ssl_policy" "default" {
  name    = "default-ssl-policy"
  profile = "MODERN" # Mandatory for SOC2 compliance
  min_tls_version = "TLS_1_2" # Mandatory for SOC2 compliance
}
