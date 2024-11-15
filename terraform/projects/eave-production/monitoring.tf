module "monitoring" {
  source           = "../../modules/monitoring"
  slack_auth_token = var.GCP_MONITORING_SLACK_AUTH_TOKEN
  uptime_checks = [
    {
      service  = "dashboard"
      name     = "Eave Dashboard uptime check"
      severity = "CRITICAL"
      host     = "dashboard.${local.root_domain}"
      path     = "/status"
      matches_json_path = {
        content   = "OK"
        json_path = "$.status"
      }
    },
    {
      service  = "core-api"
      name     = "Eave Core API uptime check"
      severity = "CRITICAL"
      host     = "api.${local.root_domain}"
      path     = "/status"
      matches_json_path = {
        content   = "OK"
        json_path = "$.status"
      }
    },
    {
      service         = "marketing"
      name            = "Eave Marketing Website uptime check"
      severity        = "CRITICAL"
      host            = "www.${local.root_domain}"
      path            = "/"
      contains_string = "Eave" // :shrug: probably not great
    },
    {
      service         = "cdn"
      name            = "Eave CDN uptime check"
      severity        = "CRITICAL"
      host            = "cdn.${local.root_domain}"
      path            = "/status.json"
      contains_string = "OK"
    },
  ]
}
