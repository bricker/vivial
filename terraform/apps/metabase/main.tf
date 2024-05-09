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

module "metabase_instances" {
  source = "./instance"
  for_each = { for instance in var.metabase_instances: instance.metabase_instance_id => instance }

  metabase_instance_id = each.value.metabase_instance_id
  team_id = each.value.team_id
  project = var.project

  cloudsql_instance_name = var.cloudsql_instance_name

  kube_namespace_name = var.kube_namespace_name
  shared_metabase_secret_name = kubernetes_secret.shared.metadata[0].name
  shared_metabase_config_map_name = kubernetes_config_map.shared.metadata[0].name

  iap_oauth_client_credentials_secret_name = kubernetes_secret.iap_oauth_credentials.metadata[0].name
  iap_oauth_client_secret_secret_name = kubernetes_secret.iap_oauth_client_secret.metadata[0].name
  iap_oauth_client_id = var.IAP_OAUTH_CLIENT_CREDENTIALS.client_id

  MB_INSTANCE_SECRETS = var.MB_INSTANCE_SECRETS[each.value.metabase_instance_id]
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
    for mbid, instance in module.metabase_instances:
      "serviceAccount:${instance.service_accounts.gsa.email}"
  ]
}
