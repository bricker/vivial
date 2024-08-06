output "bucket_ref" {
  value = google_storage_bucket.default.id
}

output "domain" {
  value = local.domain
}