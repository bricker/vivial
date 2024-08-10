# https://cloud.google.com/kubernetes-engine/docs/how-to/hardening-your-cluster#use_least_privilege_sa

resource "google_service_account" "gke_node" {
  account_id   = "gke-node"
  display_name = "Kubernetes Node"
  description = "Service account for Kubernetes nodes"
}

module "custom_gke_node_role" {
  source  = "../../modules/custom_role"
  role_id = "eave.gkeNode"
  title   = "GKE Node"
  base_roles = [
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/monitoring.viewer",
    "roles/stackdriver.resourceMetadata.writer",
    "roles/autoscaling.metricsWriter",
  ]
  members = [
    "serviceAccount:${google_service_account.gke_node.email}"
  ]
}

resource "google_artifact_registry_repository_iam_binding" "gke_node_role" {
  repository = data.google_artifact_registry_repository.docker.name
  role = module.custom_gke_node_role.role_id
  members = [
    "serviceAccount:${google_service_account.gke_node.email}",
  ]
}
