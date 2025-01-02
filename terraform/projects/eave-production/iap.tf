module "iap" {
  source = "../../modules/iap"
  dns_domain = local.dns_domain
  application_title = "Eave"
  gateways = local.iap_gateways
}

moved {
  from = google_iap_brand.project
  to = module.iap.google_iap_brand.project
}

moved {
  from = google_iap_client.default
  to = module.iap.google_iap_client.default
}

moved {
  from = google_iap_settings.admin_gw
  to = module.iap.google_iap_settings.gateway["admin_gw"]
}

moved {
  from = google_iap_settings.core_gw
  to = module.iap.google_iap_settings.gateway["core_iap_gw"]
}
