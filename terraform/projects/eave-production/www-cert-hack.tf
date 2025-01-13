moved {
  from = google_certificate_manager_dns_authorization.dashboard
  to   = module.dashboard_app.module.certificate.google_certificate_manager_dns_authorization.default[0]
}

moved {
  from = google_certificate_manager_certificate.dashboard
  to   = module.dashboard_app.module.certificate.google_certificate_manager_certificate.default
}

moved {
  from = google_certificate_manager_certificate_map_entry.dashboard
  to   = module.dashboard_app.module.certificate.google_certificate_manager_certificate_map_entry.default
}
