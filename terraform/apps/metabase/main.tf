resource "google_compute_global_address" "default" {
  name         = "metabase-instances"
  address_type = "EXTERNAL"
}

resource "google_dns_record_set" "default" {
  managed_zone = var.dns_zone.name
  name = "*.${local.domain_prefix}.${var.dns_zone.dns_name}"
  type = "A"
  ttl  = 300
  rrdatas = [google_compute_global_address.default.address]
}

locals {
  domain = join(".", [local.domain_prefix, trimsuffix(var.dns_zone.dns_name, ".")])
}

# This has to be defined outside of the metabase app modules because it's shared by all metabase instances.
module "metabase_role" {
  source      = "../../modules/custom_role"
  project = var.project
  role_id     = "eave.metabaseApp"
  title       = "Metabase App"
  description = "Permissions needed by the Metabase apps"
  base_roles  = [
    "roles/logging.logWriter",
    "roles/cloudsql.instanceUser", # for IAM auth
    "roles/cloudsql.client",
  ]

  members = [
    for mbid, sa in module.service_accounts:
      "serviceAccount:${sa.gsa.email}"
  ]
}
