module "metabase_instances" {
  source = "./instance"
  for_each = toset(var.metabase_instances)

  metabase_instance_id = each.key
  project = var.project
  kube_namespace_name = var.kube_namespace_name
  cloudsql_instance_name = var.cloudsql_instance_name
  shared_metabase_secret_name = kubernetes_secret.shared.metadata[0].name
  shared_metabase_config_map_name = kubernetes_config_map.shared.metadata[0].name

  MB_INSTANCE_SECRETS = var.MB_INSTANCE_SECRETS[each.key]
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
