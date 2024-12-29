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
      service  = "www"
      name     = "Website uptime check"
      enabled  = true
      severity = "CRITICAL"
      host     = "www-preview.${local.dns_domain}" # domain prefix is hardcoded on purpose
      path     = "/status"
      matches_json_path = {
        content   = "OK"
        json_path = "$.status"
      }
    },
    {
      service         = "www-squarespace"
      name            = "Website (Squarespace) uptime check"
      enabled         = true
      severity        = "CRITICAL"
      host            = "www.${local.dns_domain}" # domain prefix is hardcoded on purpose
      path            = "/"
      contains_string = "Eave"
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
    },
  ]
  addl_notification_channels = [
    # Bryan's phone. This type of channel can only be created in the GCP console.
    "projects/eave-production/notificationChannels/18048082649449908319"
  ]
}
