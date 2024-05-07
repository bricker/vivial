module "service_accounts" {
  source         = "../../modules/gke_app_service_account"
  project     = var.project
  kube_service_name            = local.app_name #kubernetes_service.app.metadata[0].name
  kube_namespace_name = var.kube_namespace_name
}

# Create custom role
module "app_iam_role" {
  source      = "../../modules/custom_role"
  project = var.project
  role_id     = "eave.dashboardApp"
  title       = "Eave Dashboard App"
  description = "Permissions needed by the Dashboard App"
  base_roles  = [
    "roles/logging.logWriter",
    "roles/cloudkms.signerVerifier",
    "roles/secretmanager.secretAccessor",
  ]

  members = [
    "serviceAccount:${module.service_accounts.gsa.email}"
  ]
}

module "dns" {
  source        = "../../modules/dns"
  domain_prefix = local.public_domain_prefix
  zone          = var.dns_zone
}
