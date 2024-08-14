resource "google_service_account" "thoropass_integration_sa_prod" {
  project = data.google_project.default.project_id
  account_id   = "thoropass-integration"
  display_name = "Thoropass Integration (Production)"
  description  = "Used by Thoropass for GCP integration"
}

resource "google_service_account" "thoropass_integration_sa_stg" {
  project = data.google_project.staging.project_id
  account_id   = "thoropass-integration"
  display_name = "Thoropass Integration (Staging)"
  description  = "Used by Thoropass for GCP integration"
}

resource "google_organization_iam_custom_role" "thoropass_role" {
  org_id = local.org_id
  role_id     = "eave.thoropass"
  title       = "Thoropass"
  description = "Permissions needed by Thoropass for GCP integration"
  # stage = "ALPHA" # Is this necessary? The Thoropass setup docs say to use Alpha but idk why.
  permissions = [
    "cloudbuild.builds.get",
    "cloudbuild.builds.list",
    "cloudkms.keyRings.list",
    "cloudkms.cryptoKeys.list",
    "cloudsql.backupRuns.list",
    "cloudsql.instances.get",
    "cloudsql.instances.list",
    "compute.autoscalers.list",
    "compute.disks.list",
    "compute.firewalls.list",
    "compute.images.list",
    "compute.instanceGroups.list",
    "compute.instances.list",
    "compute.projects.get",
    "container.clusters.list",
    "iam.roles.get",
    "iam.roles.list",
    "iam.serviceAccounts.get",
    "iam.serviceAccounts.getIamPolicy",
    "iam.serviceAccounts.list",
    "logging.buckets.list",
    "monitoring.alertPolicies.list",
    "monitoring.notificationChannels.get",
    "monitoring.notificationChannels.list",
    "recommender.cloudsqlIdleInstanceRecommendations.get",
    "resourcemanager.projects.get",
    "resourcemanager.projects.getIamPolicy",
    "resourcemanager.folders.getIamPolicy",
    "resourcemanager.organizations.getIamPolicy",
    "serviceusage.services.get",
    "serviceusage.services.list",
    "storage.buckets.list",
  ]
}

resource "google_organization_iam_binding" "org_thoropass_access" {
  org_id  = local.org_id
  role    = google_organization_iam_custom_role.thoropass_role.id

  members = [
    "serviceAccount:${google_service_account.thoropass_integration_sa_stg.email}",
    "serviceAccount:${google_service_account.thoropass_integration_sa_prod.email}",
  ]
}
