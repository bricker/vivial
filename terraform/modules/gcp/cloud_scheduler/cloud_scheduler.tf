variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

resource "google_cloud_scheduler_job" "run_api_documentation_job" {
  attempt_deadline = "60m"
  description      = null
  name             = "run-api-documentation"
  paused           = false
  project = var.project_id
  region           = var.region
  schedule         = "0 * * * *"
  time_zone        = "Etc/UTC"
  app_engine_http_target {
    body         = null
    headers      = {}
    http_method  = "POST"
    relative_uri = "/_/github/cron/run-api-documentation"
    app_engine_routing {
      instance = null
      service  = "github"
      version  = null
    }
  }
  retry_config {
    max_backoff_duration = "3600s"
    max_doublings        = 5
    max_retry_duration   = "0s"
    min_backoff_duration = "5s"
    retry_count          = 0
  }
  timeouts {
    create = null
    delete = null
    update = null
  }
}
