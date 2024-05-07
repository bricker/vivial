locals {
  app_name = "mb-${var.metabase_instance_id}"
  public_domain_prefix = "${var.metabase_instance_id}.mb"

  service_port = {
    name = "http"
    number = 80
  }

  app_port = {
    name = "app"
    number = 3000
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
  metabase_enterprise_version = "latest"
}