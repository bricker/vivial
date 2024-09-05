output "bucket_name" {
  value = google_storage_bucket.default.name
}

output "domain" {
  value = local.domain
}

output "url" {
  value = "https://${local.domain}"
}