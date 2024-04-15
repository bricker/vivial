variable "root_domain" {
  type = string
}

locals {
  services = {
    # eave_dashboard = {
    #   name = "Eave Dashboard uptime check"
    #   host = "dashboard.${var.root_domain}"
    #   path = "/status"
    # },
    # eave_core_api = {
    #   name = "Eave Core API uptime check"
    #   host = "api.${var.root_domain}"
    #   path = "/status"
    # },
    # metabase = {
    #   name = "Metabase uptime check"
    #   host = "metabase.${var.root_domain}"
    #   path = "/status"
    # },
  }
}

resource "google_monitoring_uptime_check_config" "uptime-check-each" {
  for_each = local.services

  checker_type     = "STATIC_IP_CHECKERS"
  display_name     = each.value.name
  period           = "60s"
  project          = var.project_id
  selected_regions = []
  timeout          = "10s"

  content_matchers {
    content = "\"OK\""
    matcher = "MATCHES_JSON_PATH"
    json_path_matcher {
      json_matcher = "EXACT_MATCH"
      json_path    = "$.status"
    }
  }
  http_check {
    body           = null
    content_type   = null
    headers        = {}
    mask_headers   = false
    path           = each.value.path
    port           = 443
    request_method = "GET"
    use_ssl        = true
    validate_ssl   = true
    accepted_response_status_codes {
      status_class = null
      status_value = 200
    }
  }
  monitored_resource {
    labels = {
      host       = each.value.host
      project_id = var.project_id
    }
    type = "uptime_url"
  }
  timeouts {
    create = null
    delete = null
    update = null
  }
}

resource "google_monitoring_alert_policy" "uptime_alert_policy_each" {
  for_each = local.services
  depends_on = [
    google_monitoring_notification_channel.slack,
    google_monitoring_uptime_check_config.uptime-check-each,
  ]

  combiner              = "OR"
  display_name          = "${each.value.name} failure"
  enabled               = true
  notification_channels = concat([google_monitoring_notification_channel.slack.name], var.addl_notification_channels)
  project               = var.project_id
  user_labels           = {}
  conditions {
    display_name = "Failure of uptime ${google_monitoring_uptime_check_config.uptime-check-each[each.key].uptime_check_id}"
    condition_threshold {
      comparison              = "COMPARISON_GT"
      denominator_filter      = null
      duration                = "60s"
      evaluation_missing_data = null
      filter                  = "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" AND metric.label.check_id=\"${google_monitoring_uptime_check_config.uptime-check-each[each.key].uptime_check_id}\" AND resource.type=\"uptime_url\""
      threshold_value         = 1
      aggregations {
        alignment_period     = "1200s"
        cross_series_reducer = "REDUCE_COUNT_FALSE"
        group_by_fields      = ["resource.label.*"]
        per_series_aligner   = "ALIGN_NEXT_OLDER"
      }
      trigger {
        count   = 1
        percent = 0
      }
    }
  }
  timeouts {
    create = null
    delete = null
    update = null
  }
}
