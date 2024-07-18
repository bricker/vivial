output "bucket_name" {
  value = google_storage_bucket.cdn.name
}

output "domain" {
  value = locals.domain
}