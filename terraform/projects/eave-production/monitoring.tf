module "monitoring" {
  source           = "../../modules/monitoring"
  slack_auth_token = var.GCP_MONITORING_SLACK_AUTH_TOKEN
  uptime_checks = [
    {
      service  = "core-api"
      name     = "Core API uptime check"
      enabled  = true
      severity = "CRITICAL"
      host     = "api.${local.dns_domain}" # domain prefix is hardcoded on purpose
      path     = "/status"
      matches_json_path = {
        content   = "OK"
        json_path = "$.status"
      }
    },
    {
      service         = "www"
      name            = "Website uptime check"
      enabled         = true
      severity        = "CRITICAL"
      host            = "www.${local.dns_domain}" # domain prefix is hardcoded on purpose
      path            = "/"
      contains_string = "Eave" // :shrug: probably not great
    },
    {
      service  = "cdn"
      name     = "CDN uptime check"
      enabled  = true
      severity = "CRITICAL"
      host     = "cdn.${local.dns_domain}" # domain prefix is hardcoded on purpose
      path     = "/status"
      matches_json_path = {
        content   = "OK"
        json_path = "$.status"
      }
    },
  ]
}
