resource "google_project_iam_custom_role" "eave_app" {
  role_id     = "eaveApp"
  title       = "Eave App"
  description = "Standard permissions needed by all Eave apps"
  permissions = [
    "cloudkms.cryptoKeyVersions.useToSign",
    "cloudkms.cryptoKeyVersions.viewPublicKey",
    "cloudtasks.tasks.create",
    "logging.logEntries.create",
    "secretmanager.versions.access",
    "pubsub.topics.publish",
  ]
}