module "service_accounts" {
  source              = "../../modules/gke_app_service_account"
  kube_service_name   = module.kubernetes_service.name
  kube_namespace_name = var.kube_namespace_name
}

# Create custom role
module "app_iam_role" {
  source      = "../../modules/custom_role"
  role_id     = "eave.coreApiApp"
  title       = "Core API App"
  description = "Permissions needed by the Core API App"
  base_roles = [
    "roles/logging.logWriter",
    "roles/cloudkms.signerVerifier",
    "roles/secretmanager.secretAccessor",
    "roles/bigquery.dataOwner",
    "roles/cloudsql.instanceUser", # for IAM auth
    "roles/cloudsql.client",
    "roles/dlp.user",
  ]

  members = [
    "serviceAccount:${data.google_service_account.gke_gsa.email}"
  ]
}

resource "google_sql_database" "app" {
  name     = "eave"
  instance = data.google_sql_database_instance.given.name
  deletion_policy = "ABANDON"
}

resource "google_sql_user" "app" {
  instance        = data.google_sql_database_instance.given.name
  name            = trimsuffix(data.google_service_account.gke_gsa.email, ".gserviceaccount.com")
  type            = "CLOUD_IAM_SERVICE_ACCOUNT"
  password        = null # only IAM supported
  deletion_policy = "ABANDON"
}

resource "google_compute_global_address" "a_addrs" {
  count = 1
  name         = "${local.app_name}-${count.index}"
  address_type = "EXTERNAL"
}

resource "google_dns_record_set" "default" {
  managed_zone = data.google_dns_managed_zone.given.name
  name         = "${local.domain_prefix}.${data.google_dns_managed_zone.given.dns_name}"
  type         = "A"
  ttl          = 300
  rrdatas      = [
    for addr in google_compute_global_address.a_addrs: addr.address
  ]
}

module "api_certificate" {
  source          = "../../modules/certificate_manager"
  certificate_map_name = var.certificate_map_name
  cert_name       = local.app_name
  entry_name      = local.app_name
  hostname        = local.domain
}
