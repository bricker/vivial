module "custom_secret_accessor_role" {
  source  = "../../modules/custom_role"
  role_id = "eave.secretAccessor"
  title   = "Access to secret manager secrets, for use with secret iam bindings"
  base_roles = [
    "roles/secretmanager.secretAccessor"
  ]
}

module "secret_manager_secrets" {
  source = "../../modules/secret_manager"

  for_each = {
    "EAVE_GOOGLE_OAUTH_CLIENT_CREDENTIALS_JSON_B64" = {
      data = var.EAVE_GOOGLE_OAUTH_CLIENT_CREDENTIALS_JSON_B64,
      accessors = [module.core_api_app.],
    },
    "SLACK_SYSTEM_BOT_TOKEN"                        = {
      data = var.SLACK_SYSTEM_BOT_TOKEN,
      accessors = [],
    },
    "OPENAI_API_KEY"                                = {
      data = var.OPENAI_API_KEY
      accessors = [],
    },
  }

  secret_id   = each.key
  secret_data = each.value

  accessors = []
}