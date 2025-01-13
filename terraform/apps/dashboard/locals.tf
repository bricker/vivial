locals {
  app_name = "dashboard"
  domain   = trimsuffix(google_dns_record_set.default.name, ".")

  service_port = {
    name   = "http"
    number = 80
  }

  app_port = {
    name   = "app"
    number = 8000
  }
}