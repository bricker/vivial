module "iap" {
  source            = "../../modules/iap"
  dns_domain        = local.dns_domain
  application_title = "Eave"
  backend_services = data.google_compute_backend_service.k8s_backend_services
}

moved {
  from = google_iap_brand.project
  to   = module.iap.google_iap_brand.project
}

moved {
  from = google_iap_client.default
  to   = module.iap.google_iap_client.default
}

moved {
  from = google_iap_settings.admin_gw
  to   = module.iap.google_iap_settings.gateways["admin"]
}

moved {
  from = google_iap_settings.core_gw
  to   = module.iap.google_iap_settings.gateways["core_api_iap"]
}
