data "google_project" "default" {}

data "google_compute_network" "given" {
  name = var.network_name
}

data "google_artifact_registry_repository" "docker" {
  location      = var.docker_repository_ref.location
  repository_id = var.docker_repository_ref.repository_id
}

data "google_iam_role" "custom_gke_node_role" {
  name = module.custom_gke_node_role.name
}