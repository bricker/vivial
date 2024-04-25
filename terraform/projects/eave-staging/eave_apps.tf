locals {
  customRoles = {
    "eave.eaveApp" = {
      title       = "Eave App"
      description = "Standard permissions needed by all Eave apps"
      base_roles = [
        "roles/logging.logWriter",
        "roles/cloudkms.signerVerifier",
        "roles/secretmanager.secretAccessor",
      ]
    }
    "eave.eaveAppCloudsqlIamClient" = {
      title       = "Eave App CloudSQL IAM Client"
      description = "Eave App that needs to connect/use Cloud SQL via IAM"
      base_roles = [
        "roles/cloudsql.instanceUser", # for IAM auth
        "roles/cloudsql.client",
      ]
    }
    "eave.metabaseApp" = {
      title       = "Metabase App"
      description = "Permissions needed by the Metabase apps"
      base_roles = [
        "roles/logging.logWriter",
      ]
    }
    "eave.playgroundApp" = {
      role_id     = "eave.playgroundApp"
      title       = "Eave Playground App"
      description = "Permissions for Eave Playground Apps"
      base_roles = [
        "roles/logging.logWriter",
      ]
    }
  }

  apps = {
    "core-api" = {
      domain_prefix = "api"
      custom_roles = [
        "eave.eaveApp",
        "eave.eaveAppCloudsqlIamClient"
      ]
    }
    "dashboard" = {
      domain_prefix = "dashboard"
      custom_roles = [
        "eave.eaveApp"
      ]
    }
    "metabase" = {
      domain_prefix = "metabase"
      custom_roles = [
        "eave.metabaseApp",
        "eave.eaveAppCloudsqlIamClient",
      ]
    }
    "playground-todoapp" = {
      domain_prefix = "playground-todoapp"
      custom_roles = [
        "eave.playgroundApp",
        "eave.eaveAppCloudsqlIamClient",
      ]
    }
  }
}

# Create custom roles
module "custom_roles" {
  for_each = local.customRoles

  source      = "../../modules/custom_role"
  role_id     = each.key
  title       = each.value.title
  description = each.value.description
  base_roles = each.value.base_roles
}

# Create app service accounts
module "apps_service_accounts" {
  for_each = local.apps

  source         = "../../modules/gke_app_service_account"
  project_id     = local.project_id
  app            = each.key
  kube_namespace = "eave"
}

# Bind the custom roles to necessary service accounts. This is authoritative.
resource "google_project_iam_binding" "custom_role_bindings" {
  for_each = module.custom_roles

  project = local.project_id
  role    = each.value.role.id

  members = [
    for app, props in local.apps :
    "serviceAccount:${module.apps_service_accounts[app].service_account.email}"
    if contains(props.custom_roles, each.value.role.role_id)
  ]
}

module "dns_apps" {
  for_each = local.apps

  source        = "../../modules/dns"
  domain_prefix = each.value.domain_prefix
  zone          = module.dns_zone_base_domain.zone
}
