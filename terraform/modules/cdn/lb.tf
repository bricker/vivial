resource "google_compute_backend_bucket" "default" {
  lifecycle {
    prevent_destroy = true
  }

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

# resource "random_id" "url_signature" {
#   byte_length = 16
# }

# resource "google_compute_backend_bucket_signed_url_key" "backend_key" {
#   name           = "${var.name}-backend-key"
#   key_value      = random_id.url_signature.b64_url
#   backend_bucket = google_compute_backend_bucket.default.name
# }

resource "google_compute_url_map" "default" {
  lifecycle {
    prevent_destroy = true
  }

  name            = "${var.name}-lb-urlmap"
  default_service = google_compute_backend_bucket.default.id
}

resource "google_compute_target_https_proxy" "default" {
  lifecycle {
    prevent_destroy = true
  }

  name            = "${var.name}-lb-https-proxy"
  url_map         = google_compute_url_map.default.id
  certificate_map = "//certificatemanager.googleapis.com/${var.google_certificate_manager_certificate_map.id}"
  ssl_policy      = var.google_compute_ssl_policy.name
}

resource "google_compute_global_forwarding_rule" "default" {
  lifecycle {
    prevent_destroy = true
  }

  name                  = "${var.name}-lb-forwarding-rule"
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  port_range            = "443"
  target                = google_compute_target_https_proxy.default.id
  ip_address            = google_compute_global_address.default.id
}

moved {
  from = module.cdn_certificate
  to   = module.certificate
}

module "certificate" {
  source                                     = "../../modules/certificate_manager"
  google_certificate_manager_certificate_map = var.google_certificate_manager_certificate_map
  cert_name                                  = var.name
  entry_name                                 = var.name
  hostname                                   = local.domain
}