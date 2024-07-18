resource "google_monitoring_notification_channel" "slack" {
  description  = null
  display_name = "Slack Alerts"
  enabled      = true
  force_delete = false
  labels = {
    channel_name = "#alerts-gcp"
    team         = "Eave"
  }
  sensitive_labels {
    auth_token = var.slack_auth_token
  }
  type        = "slack"
}
