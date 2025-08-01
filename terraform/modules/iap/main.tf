resource "google_iap_brand" "project" {
  application_title = var.application_title
  support_email     = "support@eave.fyi"
}

resource "google_iap_client" "default" {
  brand        = google_iap_brand.project.id
  display_name = "Default IAP Client"
}

moved {
  from = google_iap_settings.gateways
  to   = google_iap_settings.backend_services
}

resource "google_iap_settings" "backend_services" {
  for_each = var.backend_services

  name = "projects/${data.google_project.default.number}/iap_web/compute/services/${each.value.name}"

  access_settings {
    cors_settings {
      allow_http_options = true
    }
    allowed_domains_settings {
      enable  = true
      domains = ["*.${var.dns_domain}"]
    }
    oauth_settings {
      login_hint = "eave.fyi"
    }
    # reauth_settings {
    #   max_age = "2592000s"
    #   method = "ENROLLED_SECOND_FACTORS"
    #   policy_type = "DEFAULT"
    # }
  }
  application_settings {
    cookie_domain = var.dns_domain
  }
}
