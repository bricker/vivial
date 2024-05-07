# locals {
#   customServiceAccountRoles = {
#     "eave.metabaseUiBigQueryAccessor" = {
#       title       = "Metabase UI BigQuery Accessor"
#       description = "Metabase UI BigQuery Accessor"
#       base_roles = [
#         "roles/bigquery.dataViewer",
#         "roles/bigquery.jobUser",
#       ]
#     }
#   }

#   serviceAccounts = {
#     "metabase-ui-bq-accessor" = {
#       title = "Metabase UI BigQuery Accessor"
#       description = "Used by the Metabase UI to access the BQ datasets"
#       custom_roles = [
#         "eave.metabaseUiBigQueryAccessor",
#       ]
#     }
#   }
# }

# # Create custom roles
# module "service_accounts_custom_roles" {
#   for_each = local.customServiceAccountRoles

#   source      = "../../modules/custom_role"
#   role_id     = each.key
#   title       = each.value.title
#   description = each.value.description
#   base_roles  = each.value.base_roles
# }

# # Create service accounts
# resource "google_service_account" "addl_service_accounts" {
#   for_each = local.serviceAccounts
#   account_id   = each.key
#   display_name = each.value.title
#   description = each.value.description
# }

# # Bind the custom roles to necessary service accounts. This is authoritative.
# resource "google_project_iam_binding" "service_accounts_custom_role_bindings" {
#   for_each = module.service_accounts_custom_roles

#   project = local.project.id
#   role    = each.value.role.id

#   members = [
#     for acct, props in local.serviceAccounts :
#     "serviceAccount:${google_service_account.addl_service_accounts[acct].email}"
#     if contains(props.custom_roles, each.value.role.role_id)
#   ]
# }
