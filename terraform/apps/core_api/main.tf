module "service_accounts" {
  source         = "../../modules/gke_app_service_account"
  project     = var.project
  kube_service_name            = module.kubernetes_service.name
  kube_namespace_name = var.kube_namespace_name
}

# Create custom role
module "app_iam_role" {
  source      = "../../modules/custom_role"
  project = var.project
  role_id     = "eave.coreApiApp"
  title       = "Core API App"
  description = "Permissions needed by the Core API App"
  base_roles  = [
    "roles/logging.logWriter",
    "roles/cloudkms.signerVerifier",
    "roles/secretmanager.secretAccessor",
    "roles/bigquery.dataOwner",
    "roles/cloudsql.instanceUser", # for IAM auth
    "roles/cloudsql.client",
  ]

  members = [
    "serviceAccount:${module.service_accounts.gsa.email}"
  ]
}

resource "google_sql_database" "app" {
  name     = "eave"
  instance = var.cloudsql_instance_name
}

resource "google_sql_user" "app" {
  instance        = var.cloudsql_instance_name
  name            = trimsuffix(module.service_accounts.gsa.email, ".gserviceaccount.com")
  type            = "CLOUD_IAM_SERVICE_ACCOUNT"
  password        = null # only IAM supported
  deletion_policy = "ABANDON"
}

resource "google_compute_global_address" "default" {
  name         = "core-api"
  address_type = "EXTERNAL"
}

# Two DNS records are defined here:
# 1. api.eave.fyi
# 2. embed.eave.fyi
# Both of these go to the same IP address, which maps to the Core API load balancer
# The load balancer is configured such that requests to embed.eave.fyi get their path rewritten for compatibility with the Metabase auth proxy.
resource "google_dns_record_set" "default" {
  managed_zone = var.dns_zone.name
  name = "${local.domain_prefix}.${var.dns_zone.dns_name}"
  type = "A"
  ttl  = 300
  rrdatas = [google_compute_global_address.default.address]
}

resource "google_dns_record_set" "embed" {
  managed_zone = var.dns_zone.name
  name = "${local.embed_domain_prefix}.${var.dns_zone.dns_name}"
  type = "A"
  ttl  = 300
  rrdatas = [google_compute_global_address.default.address]
}

locals {
  domain = trimsuffix(google_dns_record_set.default.name, ".")
  embed_domain = trimsuffix(google_dns_record_set.embed.name, ".")
}

module "api_certificate" {
  source = "../../modules/certificate_manager"
  certificate_map = var.certificate_map_name
  cert_name = local.app_name
  entry_name = local.app_name
  hostname = local.domain
}

module "embed_certificate" {
  source = "../../modules/certificate_manager"
  certificate_map = var.certificate_map_name
  cert_name = "embed"
  entry_name = "embed"
  hostname = local.embed_domain
}
