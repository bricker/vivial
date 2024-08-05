# # https://cloud.google.com/cdn/docs/cdn-terraform-examples


resource "google_storage_bucket" "default" {
  name                        = "${var.name}.${var.root_domain}"
  default_event_based_hold    = false
  enable_object_retention     = false
  force_destroy               = false
  labels                      = {}
  location                    = "US"
  requester_pays              = false
  rpo                         = null
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  public_access_prevention = "inherited"

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
  bucket = google_storage_bucket.default.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

# # Create custom role
# module "cdn_iam_role" {
#   source      = "../../modules/custom_role"
#   role_id     = "eave.cdn"
#   title       = "CDN"
#   description = "Permissions needed by the Cloud CDN to access backend buckets"
#   base_roles = [
#     "roles/storage.objectViewer",
#   ]

#   members = [
#     "serviceAccount:service-${data.google_project.default.number}@cloud-cdn-fill.iam.gserviceaccount.com"
#   ]
# }
