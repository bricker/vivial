variable "slack_auth_token" {
  type = string
  sensitive = true
}

output "slack_notification_channel_name" {
  value = google_monitoring_notification_channel.slack.name
}

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
  project     = "eave-production"
  type        = "slack"
  user_labels = {}
  timeouts {
    create = null
    delete = null
    update = null
  }
}
