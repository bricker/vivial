module "secret_manager_secrets" {
  source = "../secret_manager"

  for_each = var.secrets

  secret_id                 = each.key
  secret_data               = each.value.data
  secret_accessor_role_name = var.secret_accessor_role_name
  accessors                 = each.value.accessors
}