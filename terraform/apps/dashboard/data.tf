data "google_project" "default" {}

data "google_artifact_registry_repository" "docker" {
  location      = var.docker_repository_ref.location
  repository_id = var.docker_repository_ref.repository_id
}

data "google_service_account" "app_service_account" {
  account_id = module.service_accounts.gsa_account_id
}
