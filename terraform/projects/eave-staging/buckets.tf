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
