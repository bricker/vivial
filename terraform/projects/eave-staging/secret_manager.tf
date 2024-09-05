module "secret_manager_secrets" {
  source = "../../modules/secret_manager"

  for_each = {
    "EAVE_GOOGLE_OAUTH_CLIENT_CREDENTIALS_JSON_B64" = {
      data = var.EAVE_GOOGLE_OAUTH_CLIENT_CREDENTIALS_JSON_B64,
      accessors = [
        data.google_service_account.app_service_accounts[module.core_api_app.service_account_id].member,
      ],
    },
    "SLACK_SYSTEM_BOT_TOKEN" = {
      data = var.SLACK_SYSTEM_BOT_TOKEN,
      accessors = [
        data.google_service_account.app_service_accounts[module.core_api_app.service_account_id].member,
        data.google_service_account.app_service_accounts[module.dashboard_app.service_account_id].member,
      ],
    },
    "OPENAI_API_KEY" = {
      data = var.OPENAI_API_KEY
      accessors = [
        data.google_service_account.app_service_accounts[module.core_api_app.service_account_id].member,
        data.google_service_account.app_service_accounts[module.playground_quizapp.service_account_id].member,
        data.google_service_account.app_service_accounts[module.playground_todoapp.service_account_id].member,
      ],
    },
  }

  secret_id               = each.key
  secret_data             = each.value.data
  secret_accessor_role_name = module.project_base.secret_accessor_role_name
  accessors               = each.value.accessors
}