module "monitoring" {
  source = "../../modules/monitoring"
  slack_auth_token = var.GCP_MONITORING_SLACK_AUTH_TOKEN
  uptime_checks = [
    {
      service = "dashboard"
      name = "Eave Dashboard uptime check"
      host = "dashboard.${local.root_domain}"
      path = "/status"
      severity = "CRITICAL"
    },
    {
      service = "core-api"
      name = "Eave Core API uptime check"
      host = "api.${local.root_domain}"
      path = "/status"
      severity = "CRITICAL"
    },
    {
      service = "cdn"
      name = "Eave CDN uptime check"
      host = "cdn.${local.root_domain}"
      path = "/collector.js"
      severity = "CRITICAL"
    },
    {
      service = "marketing"
      name = "Eave Marketing Website uptime check"
      host = "www.${local.root_domain}"
      path = "/"
      severity = "CRITICAL"
    },
  ]
}
