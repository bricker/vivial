resource "google_compute_backend_bucket" "cdn" {
  name        = "cdn-backend"
  bucket_name = google_storage_bucket.cdn.name
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

resource "google_compute_url_map" "cdn" {
  name            = "cdn-lb-urlmap"
  default_service = google_compute_backend_bucket.cdn.id
}

resource "google_compute_target_https_proxy" "cdn" {
  name    = "cdn-lb-https-proxy"
  url_map = google_compute_url_map.cdn.id
  certificate_map = "//certificatemanager.googleapis.com/${var.certificate_map.id}"
}

resource "google_compute_global_forwarding_rule" "cdn" {
  name                  = "cdn-lb-forwarding-rule"
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  port_range            = "443"
  target                = google_compute_target_https_proxy.cdn.id
  ip_address            = google_compute_global_address.cdn.id
}
