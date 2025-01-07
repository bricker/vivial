moved {
  from = module.iap.google_iap_settings.backend_services["api"]
  to = module.iap.google_iap_settings.backend_services["core-api"]
}
module "iap" {
  source            = "../../modules/iap"
  dns_domain        = local.dns_domain
  application_title = "Eave (Staging)"
  backend_services  = data.google_compute_backend_service.k8s_backend_services
}
