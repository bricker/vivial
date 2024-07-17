# # https://cloud.google.com/cdn/docs/cdn-terraform-examples

resource "google_storage_bucket" "cdn" {
  name                        = "cdn.${local.project.root_domain}"
  default_event_based_hold    = false
  enable_object_retention     = false
  force_destroy               = false
  labels                      = {}
  location                    = "US-CENTRAL1"
  public_access_prevention    = "inherited"
  requester_pays              = false
  rpo                         = null
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  lifecycle_rule {
    action {
      storage_class = null
      type          = "Delete"
    }
    condition {
      age                        = 0
      created_before             = null
      custom_time_before         = null
      days_since_custom_time     = 0
      days_since_noncurrent_time = 0
      matches_prefix             = []
      matches_storage_class      = []
      matches_suffix             = []
      no_age                     = false
      noncurrent_time_before     = null
      num_newer_versions         = 3
      with_state                 = "ARCHIVED"
    }
  }
  soft_delete_policy {
    retention_duration_seconds = 604800
  }
  versioning {
    enabled = true
  }
}

resource "google_storage_bucket_iam_member" "cdn_allusers" {
  bucket = google_storage_bucket.cdn.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}


# resource "google_compute_global_address" "cdn" {
#   name = "cdn"
# }

# resource "google_dns_record_set" "cdn" {
#   managed_zone = var.dns_zone.name
#   name         = "cdn.${var.dns_zone.dns_name}"
#   type         = "A"
#   ttl          = 300
#   rrdatas      = [google_compute_global_address.default.address]
# }

# locals {
#   domain = trimsuffix(google_dns_record_set.cdn.name, ".")
# }

# module "api_certificate" {
#   source          = "../../modules/certificate_manager"
#   certificate_map = var.certificate_map_name
#   cert_name       = "cdn"
#   entry_name      = "cdn"
#   hostname        = local.domain
# }


# resource "google_compute_backend_bucket" "cdn" {
#   name        = "cdn-backend"
#   bucket_name = google_storage_bucket.cdn.name
#   enable_cdn  = true
#   cdn_policy {
#     cache_mode        = "CACHE_ALL_STATIC"
#     client_ttl        = 3600
#     default_ttl       = 3600
#     max_ttl           = 86400
#     negative_caching  = true
#     serve_while_stale = 86400
#   }
# }

# resource "google_compute_url_map" "cdn" {
#   name            = "http-lb"
#   default_service = google_compute_backend_bucket.cdn.id
# }

# resource "google_compute_target_https_proxy" "cdn" {
#   name    = "https-lb-proxy"
#   url_map = google_compute_url_map.cdn.id
#   certificate_map = var.certificate_map_name
# }

# resource "google_compute_global_forwarding_rule" "cdn" {
#   name                  = "http-lb-forwarding-rule"
#   ip_protocol           = "TCP"
#   load_balancing_scheme = "EXTERNAL_MANAGED"
#   port_range            = "80"
#   target                = google_compute_target_http_proxy.cdn.id
#   ip_address            = google_compute_global_address.cdn.id
# }
