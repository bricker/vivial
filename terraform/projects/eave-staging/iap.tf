module "iap" {
  source = "../../modules/iap"
  dns_domain = local.dns_domain
  application_title = "Eave (Staging)"
  gateways = data.google_compute_backend_service.gateways
}
