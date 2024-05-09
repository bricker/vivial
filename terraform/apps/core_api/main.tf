# module "certificate_manager" {
#   source = "../../modules/certificate_manager"
# }

module "service_accounts" {
  source         = "../../modules/gke_app_service_account"
  project     = var.project
  kube_service_name            = kubernetes_service.app.metadata[0].name
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
# 2. mbproxy.eave.fyi
# Both of these go to the same IP address, which maps to the Core API load balancer
# The load balancer is configured such that requests to mbproxy.eave.fyi get their path rewritten for compatibility with the Metabase auth proxy.
resource "google_dns_record_set" "default" {
  managed_zone = var.dns_zone.name
  name = "${local.domain_prefix}.${var.dns_zone.dns_name}"
  type = "A"
  ttl  = 300
  rrdatas = [google_compute_global_address.default.address]
}

resource "google_dns_record_set" "mbproxy" {
  managed_zone = var.dns_zone.name
  name = "${local.mbproxy_domain_prefix}.${var.dns_zone.dns_name}"
  type = "A"
  ttl  = 300
  rrdatas = [google_compute_global_address.default.address]
}

locals {
  domain = trimsuffix(google_dns_record_set.default.name, ".")
  mbproxy_domain = trimsuffix(google_dns_record_set.mbproxy.name, ".")
}
