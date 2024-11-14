import {
  id = "SENDGRID_API_KEY"
  to = module.app_secrets.module.secret_manager_secrets["SENDGRID_API_KEY"].google_secret_manager_secret.default
}

import {
  id = "projects/eave-staging/secrets/SENDGRID_API_KEY/versions/1"
  to = module.app_secrets.module.secret_manager_secrets["SENDGRID_API_KEY"].google_secret_manager_secret_version.default
}

module "app_secrets" {
  source = "../../modules/app_secrets"

  secrets = {
    SLACK_SYSTEM_BOT_TOKEN = {
      data = var.SLACK_SYSTEM_BOT_TOKEN,
      accessors = [
        data.google_service_account.app_service_accounts[module.core_api_app.service_account_id].member,
        data.google_service_account.app_service_accounts[module.dashboard_app.service_account_id].member,
      ],
    },
    OPENAI_API_KEY = {
      data = var.OPENAI_API_KEY
      accessors = [
        data.google_service_account.app_service_accounts[module.core_api_app.service_account_id].member,
        data.google_service_account.app_service_accounts[module.dashboard_app.service_account_id].member,
      ],
    },
    SENDGRID_API_KEY = {
      data = var.SENDGRID_API_KEY
      accessors = [
        data.google_service_account.app_service_accounts[module.core_api_app.service_account_id].member,
      ],
    },
    GOOGLE_PLACES_API_KEY = {
      data = var.GOOGLE_PLACES_API_KEY
      accessors = [
        data.google_service_account.app_service_accounts[module.core_api_app.service_account_id].member,
      ],
    },
    EVENTBRITE_API_KEY = {
      data = var.EVENTBRITE_API_KEY
      accessors = [
        data.google_service_account.app_service_accounts[module.core_api_app.service_account_id].member,
      ],
    },
  }

  secret_accessor_role_name = module.project_base.secret_accessor_role_name
}
