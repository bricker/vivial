variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

resource "google_cloud_tasks_queue" "slack_events_processor_queue" {
  location = var.region
  project  = var.project_id
  name     = "slack-events-processor"

  app_engine_routing_override {
    instance = null
    service  = "slack"
    version  = null
  }
  rate_limits {
    max_concurrent_dispatches = 1000
    max_dispatches_per_second = 500
  }
  retry_config {
    max_attempts       = 3
    max_backoff        = "3600s"
    max_doublings      = 16
    max_retry_duration = null
    min_backoff        = "0.100s"
  }
  stackdriver_logging_config {
    sampling_ratio = 1
  }
  timeouts {
    create = null
    delete = null
    update = null
  }
}

resource "google_cloud_tasks_queue" "github_events_processor_queue" {
  location = var.region
  project  = var.project_id
  name     = "github-events-processor"
  app_engine_routing_override {
    instance = null
    service  = "github"
    version  = null
  }
  rate_limits {
    max_concurrent_dispatches = 1000
    max_dispatches_per_second = 500
  }
  retry_config {
    max_attempts       = 3
    max_backoff        = "3600s"
    max_doublings      = 16
    max_retry_duration = null
    min_backoff        = "0.100s"
  }
  stackdriver_logging_config {
    sampling_ratio = 1
  }
  timeouts {
    create = null
    delete = null
    update = null
  }
}
