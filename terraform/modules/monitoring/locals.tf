locals {
  services = {
    dashboard = {
      name = "Eave Dashboard uptime check"
      host = "dashboard.${var.project.root_domain}"
      path = "/status"
    },
    core_api = {
      name = "Eave Core API uptime check"
      host = "api.${var.project.root_domain}"
      path = "/status"
    },
    # metabase = {
    #   name = "Metabase uptime check"
    #   host = "metabase.${var.root_domain}"
    #   path = "/status"
    # },
  }
}