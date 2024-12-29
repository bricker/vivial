resource "google_monitoring_alert_policy" "ssl_certs_expiring" {
  combiner              = "OR"
  display_name          = "SSL certificate expiring soon"
  enabled               = true
  notification_channels = concat([google_monitoring_notification_channel.slack_uptime.name], var.addl_notification_channels)
  user_labels = {
    uptime  = "ssl_cert_expiration"
    version = "1"
  }
  conditions {
    display_name = "SSL certificate expiring soon"
    condition_threshold {
      comparison              = "COMPARISON_LT"
      denominator_filter      = null
      duration                = "600s"
      evaluation_missing_data = null
      filter                  = "metric.type=\"monitoring.googleapis.com/uptime_check/time_until_ssl_cert_expires\" AND resource.type=\"uptime_url\""
      threshold_value         = 7
      aggregations {
        alignment_period     = "1200s"
        cross_series_reducer = "REDUCE_MEAN"
        group_by_fields      = ["resource.label.*"]
        per_series_aligner   = "ALIGN_NEXT_OLDER"
      }
      trigger {
        count   = 1
        percent = 0
      }
    }
  }
}
