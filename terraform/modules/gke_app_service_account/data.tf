data "google_project" "default" {}

data "google_iam_role" "workload_identity_role" {
  name = "roles/iam.workloadIdentityUser"
}