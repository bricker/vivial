resource "google_monitoring_notification_channel" "slack_uptime" {
  display_name = "Slack - Uptime Checks"
  enabled      = true
  force_delete = false
  labels = {
    channel_name = "#alerts-uptime"
    team         = "Eave"
  }
  sensitive_labels {
    auth_token = var.slack_auth_token
  }
  type = "slack"
}

resource "google_monitoring_notification_channel" "slack_errors" {
  display_name = "Slack - App Errors"
  enabled      = true
  force_delete = false
  labels = {
    channel_name = "#alerts-errors"
    team         = "Eave"
  }
  sensitive_labels {
    auth_token = var.slack_auth_token
  }
  type = "slack"
}

resource "google_monitoring_notification_channel" "slack_systems_alerts" {
  display_name = "Slack - Systems Alerts"
  enabled      = true
  force_delete = false
  labels = {
    channel_name = "#alerts-systems"
    team         = "Eave"
  }
  sensitive_labels {
    auth_token = var.slack_auth_token
  }
  type = "slack"
}
