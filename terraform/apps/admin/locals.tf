locals {
  app_name = "admin"
  domain   = trimsuffix(google_dns_record_set.default.name, ".")

  preset_production = var.environment == "PROD"

  service_port = {
    name   = "http"
    number = 80
  }

  app_port = {
    name   = "app"
    number = 8000
  }
}