resource "google_artifact_registry_repository" "docker" {
  repository_id          = "docker"
  cleanup_policy_dry_run = true
  description            = null
  format                 = "DOCKER"
  mode = "STANDARD_REPOSITORY"
  docker_config {
    immutable_tags = false
  }
}

output "repository" {
  value = google_artifact_registry_repository.docker
}
