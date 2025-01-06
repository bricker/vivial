# https://cloud.google.com/kubernetes-engine/docs/how-to/hardening-your-cluster#use_least_privilege_sa

resource "google_service_account" "gke_node" {
  lifecycle {
    prevent_destroy = true
  }

  account_id   = "gke-node"
  display_name = "Kubernetes Node"
  description  = "Service account for Kubernetes nodes"
}

module "custom_gke_node_role" {
  source  = "../../modules/custom_role"
  role_id = "eave.gkeNode"
  title   = "GKE Node"
  base_roles = [
    "roles/container.defaultNodeServiceAccount",
    # "roles/artifactregistry.reader",
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/monitoring.viewer",
    "roles/stackdriver.resourceMetadata.writer",
    "roles/autoscaling.metricsWriter",
  ]
}

resource "google_project_iam_binding" "project_gke_node_role_members" {
  lifecycle {
    prevent_destroy = true
  }

  project = data.google_project.default.id
  role    = module.custom_gke_node_role.google_project_iam_custom_role.id

  members = var.use_default_service_account ? [
    google_service_account.gke_node.member,
    data.google_compute_default_service_account.default.member
  ] : [google_service_account.gke_node.member]
}

resource "google_artifact_registry_repository_iam_binding" "docker_repo_gke_node_role_members" {
  lifecycle {
    prevent_destroy = true
  }

  repository = data.google_artifact_registry_repository.docker.name
  role       = module.custom_gke_node_role.google_project_iam_custom_role.id

  members = var.use_default_service_account ? [
    google_service_account.gke_node.member,
    data.google_compute_default_service_account.default.member
  ] : [google_service_account.gke_node.member]
}
