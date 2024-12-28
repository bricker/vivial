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
      authenticated = false
    },
    {
      service         = "www"
      name            = "Website uptime check"
      enabled         = true
      severity        = "CRITICAL"
      host            = "www-preview.${local.dns_domain}" # domain prefix is hardcoded on purpose
      path            = "/status"
      matches_json_path = {
        content   = "OK"
        json_path = "$.status"
      }
      authenticated = false
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
      authenticated = false
    },
    {
      service  = "admin"
      name     = "Admin uptime check"
      enabled  = true
      severity = "CRITICAL"
      host     = "admin.${local.dns_domain}" # domain prefix is hardcoded on purpose
      path     = "/status"
      matches_json_path = {
        content   = "OK"
        json_path = "$.status"
      }
      authenticated = true
    },
  ]
}
