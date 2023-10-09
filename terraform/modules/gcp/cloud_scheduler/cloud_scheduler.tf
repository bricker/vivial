variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "cron_shared_secret" {
  type      = string
  sensitive = true
}

resource "google_cloud_scheduler_job" "run_api_documentation_job" {
  attempt_deadline = "3600s"
  description      = null
  name             = "run-api-documentation"
  paused           = false
  project          = var.project_id
  region           = var.region
  schedule         = "0 0 * * *"
  time_zone        = "Etc/UTC"

  app_engine_http_target {
    body = base64encode("{}")
    headers = {
      "eave-cron-shared-secret" = var.cron_shared_secret
      "eave-cron-dispatch-key"  = "run-api-documentation"
      "content-type"            = "application/json"
    }
    http_method  = "POST"
    relative_uri = "/_/github/cron"
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
