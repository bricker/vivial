data "google_project" "default" {}

data "google_certificate_manager_certificate_map" "given" {
  name = var.certificate_map_name
}

data "google_dns_managed_zone" "given" {
  name = var.dns_zone_name
}

data "google_compute_ssl_policy" "given" {
  name = var.ssl_policy_name
}

data "google_artifact_registry_repository" "docker" {
  location = var.docker_repository_ref.location
  repository_id = var.docker_repository_ref.repository_id
}

data "google_service_account" "gke_gsa" {
  account_id = module.service_accounts.gsa_ref
}
