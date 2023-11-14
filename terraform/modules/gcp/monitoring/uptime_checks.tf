variable "project_id" { type = string }
variable "region" { type = string }
variable "eave_domain_apex" { type = string }

locals {
  services = {
    eave_www = {
      name = "Eave Website uptime check"
      host = "www.${var.eave_domain_apex}"
      path = "/status"
    },
    eave_api = {
      name = "Eave Core API uptime check"
      host = "api.${var.eave_domain_apex}"
      path = "/status"
    },
    eave_github = {
      name = "Eave Github App uptime check"
      host = "apps.${var.eave_domain_apex}"
      path = "/github/status"
    }
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
