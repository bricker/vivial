output "ssl_policy_name" {
  value = google_compute_ssl_policy.default.name
}

output "network_name" {
  value = google_compute_network.primary.name
}

output "subnetwork_self_link" {
  value = google_compute_subnetwork.primary.self_link
}

output "docker_repository_ref" {
  value = {
    location = google_artifact_registry_repository.docker.location
    repository_id = google_artifact_registry_repository.docker.repository_id
  }
}

output "certificate_map_name" {
  value = google_certificate_manager_certificate_map.default.name
}

output "private_ip_range_name" {
  value = google_compute_global_address.private_ip_range.name
}
