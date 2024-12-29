module "app_secrets" {
  source = "../../modules/app_secrets"

  secrets = {
    SLACK_SYSTEM_BOT_TOKEN = {
      data = var.SLACK_SYSTEM_BOT_TOKEN,
      accessors = [
        "group:developers@eave.fyi",
      ],
    },
    SENDGRID_API_KEY = {
      data = var.SENDGRID_API_KEY
      accessors = [
        "group:developers@eave.fyi",
      ],
    },
    EVENTBRITE_API_KEY = {
      # DEPRECATED
      data = var.EVENTBRITE_API_KEY
      accessors = [
        "group:developers@eave.fyi",
      ],
    },
    EVENTBRITE_API_KEYS = {
      data = jsonencode(var.EVENTBRITE_API_KEYS)
      accessors = [
        "group:developers@eave.fyi",
      ],
    },
    STRIPE_SECRET_KEY = {
      data = var.STRIPE_SECRET_KEY
      accessors = [
        "group:developers@eave.fyi",
      ],
    },
    GOOGLE_MAPS_API_KEY = {
      data = var.GOOGLE_MAPS_API_KEY
      accessors = [
        "group:developers@eave.fyi",
      ],
    },
  }

  secret_accessor_role_name = module.project_base.secret_accessor_role_name
}
