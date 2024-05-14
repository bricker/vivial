resource "google_compute_ssl_policy" "default" {
  name    = "default-ssl-policy"
  profile = "MODERN"
}

output "policy_name" {
  value = google_compute_ssl_policy.default.name
}