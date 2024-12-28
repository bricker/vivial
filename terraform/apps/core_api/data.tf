data "google_project" "default" {}

data "google_artifact_registry_repository" "docker" {
  location      = var.docker_repository_ref.location
  repository_id = var.docker_repository_ref.repository_id
}

data "google_service_account" "cloudsql_bastion_service_account" {
  account_id = module.bastion.service_account_id
}

data "google_iam_role" "impersonator_role" {
  name = var.impersonator_role_name
}

# data "google_compute_backend_service" "admin_gw" {
#   # FIXME: This is the production one hardcoded
#   name = "gkegw1-pl44-eave-admin-80-x6dbra8rr4l6"
# }
