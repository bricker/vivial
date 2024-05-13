locals {
  app_name      = "dashboard"
  domain_prefix = "dashboard"

  service_port = {
    name   = "http"
    number = 80
  }

  app_port = {
    name   = "app"
    number = 8000
  }
}