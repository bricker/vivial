module "iap" {
  source = "../../modules/iap"
  dns_domain = local.dns_domain
  application_title = "Eave (Staging)"
  backend_services = data.google_compute_backend_service.k8s_backend_services
}
