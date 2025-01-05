output "google_compute_ssl_policy" {
  value = google_compute_ssl_policy.default
}

output "google_certificate_manager_certificate_map" {
  value = google_certificate_manager_certificate_map.default
}

output "google_compute_network" {
  value = google_compute_network.primary
}

output "google_compute_subnetwork" {
  value = google_compute_subnetwork.primary
}

output "docker_repository_ref" {
  value = {
    location      = google_artifact_registry_repository.docker.location
    repository_id = google_artifact_registry_repository.docker.repository_id
  }
}

output "private_ip_range_name" {
  value = google_compute_global_address.private_ip_range.name
}

output "usage_logs_bucket_name" {
  value = google_storage_bucket.usage_logs.name
}

output "impersonator_role_name" {
  value = module.impersonator_role.name
}

output "secret_accessor_role_name" {
  value = module.secret_accessor_role.name
}

output "compute_oslogin_role_name" {
  value = module.compute_oslogin_role.name
}

output "service_account_user_role_name" {
  value = module.service_account_user_role.name
}

output "kms_key_ring_id" {
  value = google_kms_key_ring.primary.id
}

output "google_kms_crypto_key_jws_signing_key" {
  value = google_kms_crypto_key.jws_signing_key
}

output "kms_jws_signing_key_default_version_id" {
  value = google_kms_crypto_key_version.jws_signing_key_versions[local.jws_signing_key_version_count - 1].id
}
