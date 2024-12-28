resource "google_monitoring_uptime_check_config" "uptime_checks" {
  for_each = local.uptime_checks_map

  checker_type     = "STATIC_IP_CHECKERS"
  display_name     = each.value.name
  period           = "60s"
  selected_regions = []
  timeout          = "10s"

  dynamic "content_matchers" {
    for_each = each.value.matches_json_path != null ? [each.value.matches_json_path] : []

    content {
      content = "\"${content_matchers.value.content}\""
      matcher = "MATCHES_JSON_PATH"
      json_path_matcher {
        json_matcher = "EXACT_MATCH"
        json_path    = content_matchers.value.json_path
      }
    }
  }

  dynamic "content_matchers" {
    for_each = each.value.contains_string != null ? [each.value.contains_string] : []

    content {
      content = content_matchers.value
      matcher = "CONTAINS_STRING"
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

    dynamic "service_agent_authentication" {
      # If this is an authenticated healthcheck, then use OIDC token for the server agent.
      # Otherwise don't include this block.
      for_each = each.value.authenticated ? {" _": true} : {}

      content {
        type = "OIDC_TOKEN"
      }
    }

    accepted_response_status_codes {
      status_class = null
      status_value = 200
    }
  }
  monitored_resource {
    labels = {
      host       = each.value.host
      project_id = data.google_project.default.project_id
    }
    type = "uptime_url"
  }
}

resource "google_monitoring_alert_policy" "uptime_alert_policies" {
  lifecycle {
    # This is necessary because an uptime check config can't be deleted if there is an associated alert policy.
    replace_triggered_by = [google_monitoring_uptime_check_config.uptime_checks[each.key].monitored_resource]
  }

  for_each = local.uptime_checks_map

  combiner              = "OR"
  display_name          = "FAILURE - ${each.value.name}"
  enabled               = each.value.enabled
  notification_channels = concat([google_monitoring_notification_channel.slack.name], var.addl_notification_channels)

  severity = each.value.severity

  conditions {
    display_name = "Failure of uptime ${google_monitoring_uptime_check_config.uptime_checks[each.key].uptime_check_id}"
    condition_threshold {
      comparison              = "COMPARISON_GT"
      denominator_filter      = null
      duration                = "60s"
      evaluation_missing_data = null
      filter                  = "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" AND metric.label.check_id=\"${google_monitoring_uptime_check_config.uptime_checks[each.key].uptime_check_id}\" AND resource.type=\"uptime_url\""
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
}
