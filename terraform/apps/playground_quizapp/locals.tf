locals {
  app_name      = "playground-quizapp"
  domain_prefix = "playground-quizapp"

  service_port = {
    name   = "http"
    number = 80
  }

  app_port = {
    name   = "app"
    number = 8000
  }
}