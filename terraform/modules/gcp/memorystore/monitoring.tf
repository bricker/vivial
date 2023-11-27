variable "notification_channels" {
  type = list(string)
}

resource "google_monitoring_alert_policy" "redis_cpu_usage" {
  depends_on = [ google_redis_instance.eave_redis ]
  combiner              = "OR"
  display_name          = "Cloud Redis - Redis Engine CPU utilization for eave-redis(us-central1)"
  enabled               = true
  notification_channels = var.notification_channels
  project               = var.project_id
  user_labels = {
    context       = "redis"
    instance_id   = google_redis_instance.eave_redis.name
    project_id    = var.project_id
    region        = var.region
    resource_type = "redis_instance"
  }
  alert_strategy {
    auto_close = "604800s"
  }
  conditions {
    display_name = "Cloud Memorystore Redis Instance - Redis Engine CPU utilization"
    condition_threshold {
      comparison              = "COMPARISON_GT"
      denominator_filter      = null
      duration                = "0s"
      evaluation_missing_data = null
      filter                  = "resource.type = \"redis_instance\" AND resource.labels.instance_id = \"projects/eave-production/locations/us-central1/instances/eave-redis\" AND metric.type = \"redis.googleapis.com/stats/cpu_utilization_main_thread\""
      threshold_value         = 0.9
      aggregations {
        alignment_period     = "300s"
        cross_series_reducer = "REDUCE_SUM"
        group_by_fields      = ["resource.label.instance_id", "resource.label.node_id"]
        per_series_aligner   = "ALIGN_RATE"
      }
      trigger {
        count   = 1
        percent = 0
      }
    }
  }
  documentation {
    content   = "This alert fires if the Redis Engine CPU Utilization goes above the set threshold. The utilization is measured on a scale of 0 to 1. "
    mime_type = "text/markdown"
  }
  timeouts {
    create = null
    delete = null
    update = null
  }
}

resource "google_monitoring_alert_policy" "redis_memory_usage" {
  combiner              = "OR"
  display_name          = "Cloud Redis - System Memory Utilization for eave-redis(us-central1)"
  enabled               = true
  notification_channels = var.notification_channels
  project               = var.project_id
  user_labels = {
    context       = "redis"
    instance_id   = google_redis_instance.eave_redis.name
    project_id    = var.project_id
    region        = var.region
    resource_type = "redis_instance"
  }
  alert_strategy {
    auto_close = "604800s"
  }
  conditions {
    display_name = "Cloud Memorystore Redis Instance - System Memory Usage Ratio"
    condition_threshold {
      comparison              = "COMPARISON_GT"
      denominator_filter      = null
      duration                = "0s"
      evaluation_missing_data = null
      filter                  = "resource.type = \"redis_instance\" AND resource.labels.instance_id = \"projects/eave-production/locations/us-central1/instances/eave-redis\" AND metric.type = \"redis.googleapis.com/stats/memory/system_memory_usage_ratio\""
      threshold_value         = 0.8
      aggregations {
        alignment_period     = "300s"
        cross_series_reducer = null
        group_by_fields      = []
        per_series_aligner   = "ALIGN_MEAN"
      }
      trigger {
        count   = 1
        percent = 0
      }
    }
  }
  documentation {
    content   = "This alert fires if the system memory utilization is above the set threshold. The utilization is measured on a scale of 0 to 1."
    mime_type = "text/markdown"
  }
  timeouts {
    create = null
    delete = null
    update = null
  }
}
