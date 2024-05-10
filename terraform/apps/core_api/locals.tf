locals {
  app_name = "core-api"
  domain_prefix = "api"
  viz_domain_prefix = "viz"

  service_port = {
    name = "http"
    number = 80
  }

  app_port = {
    name = "app"
    number = 8000
  }

  clousql_proxy_healthcheck_port = {
    name = "healthcheck"
    number = 9090
  }

  cloudsql_proxy_port = {
    name = "proxy"
    number = 5432
  }

  cloudsql_proxy_version = "latest"
}