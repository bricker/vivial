locals {
  app_name = "core-api"
  domain   = trimsuffix(google_dns_record_set.default.name, ".")
  eventbrite_filler_job_name = "eventbrite-filler"

  preset_production = var.environment == "PROD"

  service_port = {
    name   = "http"
    number = 80
  }

  app_port = {
    name   = "app"
    number = 8000
  }

  clousql_proxy_healthcheck_port = {
    name   = "healthcheck"
    number = 9090
  }

  cloudsql_proxy_port = {
    name   = "proxy"
    number = 5432
  }

  cloudsql_proxy_version = "latest"
}
