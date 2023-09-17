resource "google_cloud_tasks_queue" "slack-events-processor" {
  location = "us-central1"
  name     = "slack-events-processor"
  project  = var.project_id

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

resource "google_cloud_tasks_queue" "github-events-processor" {
  location = "us-central1"
  name     = "github-events-processor"
  project  = "eavefyi-dev"
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
