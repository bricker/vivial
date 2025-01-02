module "app_secrets" {
  source = "../../modules/app_secrets"

  secrets = {
    SLACK_SYSTEM_BOT_TOKEN = {
      data = var.SLACK_SYSTEM_BOT_TOKEN,
      accessors = [
        module.core_api_app.service_account.member,
        module.dashboard_app.service_account.member,
      ],
    },
    SENDGRID_API_KEY = {
      data = var.SENDGRID_API_KEY
      accessors = [
        module.core_api_app.service_account.member,
        module.dashboard_app.service_account.member,
      ],
    },
    EVENTBRITE_API_KEYS = {
      data = jsonencode(var.EVENTBRITE_API_KEYS)
      accessors = [
        module.core_api_app.service_account.member,
      ],
    },
    STRIPE_SECRET_KEY = {
      data = var.STRIPE_SECRET_KEY
      accessors = [
        module.core_api_app.service_account.member,
      ],
    },
    GOOGLE_MAPS_API_KEY = {
      data = var.GOOGLE_MAPS_API_KEY
      accessors = [
        module.core_api_app.service_account.member,
      ],
    },
  }

  secret_accessor_role_name = module.project_base.secret_accessor_role_name
}
