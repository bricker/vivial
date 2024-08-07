resource "google_compute_ssl_policy" "default" {
  name    = "default-ssl-policy"
  profile = "MODERN"
}
