module "service_accounts" {
  source              = "../../modules/gke_app_service_account"
  project             = var.project
  kube_service_name   = module.kubernetes_service.name
  kube_namespace_name = var.kube_namespace_name
}

# Create custom role
module "app_iam_role" {
  source      = "../../modules/custom_role"
  project     = var.project
  role_id     = "eave.playgroundQuizApp"
  title       = "Eave Playground Quiz App"
  description = "Permissions needed by the Playground Quiz App"
  base_roles = [
    "roles/logging.logWriter",
    "roles/secretmanager.secretAccessor",
  ]

  members = [
    "serviceAccount:${module.service_accounts.gsa.email}"
  ]
}

resource "google_compute_global_address" "default" {
  name         = local.app_name
  address_type = "EXTERNAL"
}

resource "google_dns_record_set" "default" {
  managed_zone = var.dns_zone.name
  name         = "${local.domain_prefix}.${var.dns_zone.dns_name}"
  type         = "A"
  ttl          = 300
  rrdatas      = [google_compute_global_address.default.address]
}

module "certificate" {
  source          = "../../modules/certificate_manager"
  certificate_map = var.certificate_map_name
  cert_name       = local.app_name
  entry_name      = local.app_name
  hostname        = local.domain
}
