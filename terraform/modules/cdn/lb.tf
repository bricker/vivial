resource "google_compute_backend_bucket" "default" {
  name        = "${var.name}-backend"
  bucket_name = google_storage_bucket.default.name
  enable_cdn  = true
  cdn_policy {
    cache_mode        = "CACHE_ALL_STATIC"
    client_ttl        = 3600
    default_ttl       = 3600
    max_ttl           = 86400
    negative_caching  = true
    serve_while_stale = 86400
  }
}

resource "random_id" "url_signature" {
  byte_length = 16
}

resource "google_compute_backend_bucket_signed_url_key" "backend_key" {
  name           = "${var.name}-backend-key"
  key_value      = random_id.url_signature.b64_url
  backend_bucket = google_compute_backend_bucket.default.name
}

resource "google_compute_url_map" "default" {
  name            = "${var.name}-lb-urlmap"
  default_service = google_compute_backend_bucket.default.id
}

resource "google_compute_target_https_proxy" "default" {
  name            = "${var.name}-lb-https-proxy"
  url_map         = google_compute_url_map.default.id
  certificate_map = "//certificatemanager.googleapis.com/${data.google_certificate_manager_certificate_map.given.id}"
  ssl_policy = data.google_compute_ssl_policy.given.name
}

resource "google_compute_global_forwarding_rule" "default" {
  name                  = "${var.name}-lb-forwarding-rule"
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  port_range            = "443"
  target                = google_compute_target_https_proxy.default.id
  ip_address            = google_compute_global_address.default.id
}
