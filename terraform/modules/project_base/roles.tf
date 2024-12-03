module "impersonator_role" {
  source      = "../../modules/custom_role"
  role_id     = "eave.impersonator"
  title       = "Service Account Impersonator"
  description = "Permissions needed to impersonate a service account"
  base_roles = [
    "roles/iam.serviceAccountTokenCreator",
  ]
}

module "secret_accessor_role" {
  source      = "../../modules/custom_role"
  role_id     = "eave.secretAccessor"
  title       = "Secret Manager Secret Accessor"
  description = "Permissions needed to access secret manager secrets"
  base_roles = [
    "roles/secretmanager.secretAccessor"
  ]
}

# module "cloudkms_mac_user_role" {
#   source      = "../../modules/custom_role"
#   role_id     = "eave.cloudkmsMacUser"
#   title       = "CloudKMS Signer/Verifier/Viewer"
#   description = "Permissions needed to use to sign, use to verify, and view a key"
#   base_roles = [
#     "roles/cloudkms.signerVerifier",
#     "roles/cloudkms.viewer",
#   ]
# }

module "cloudsql_user_role" {
  source      = "../../modules/custom_role"
  role_id     = "eave.cloudsqlUser"
  title       = "CloudSQL User for Apps"
  description = "Permissions needed to connect to and use CloudSQL"
  base_roles = [
    "roles/cloudsql.instanceUser", # for IAM auth
    "roles/cloudsql.client",
  ]
}

module "compute_oslogin_role" {
  # Create a role that can login to a compute VM
  source  = "../../modules/custom_role"
  role_id = "eave.computeOsLoginUser"
  title   = "Access to login to a compute VM"
  base_roles = [
    "roles/compute.osLogin",
  ]
}

module "service_account_user_role" {
  # Create a role that can login to a compute VM
  source  = "../../modules/custom_role"
  role_id = "eave.serviceAccountUser"
  title   = "Permission to run operations as a service account"
  base_roles = [
    "roles/iam.serviceAccountUser",
  ]
}