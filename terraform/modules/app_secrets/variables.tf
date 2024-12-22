variable "secret_accessor_role_name" {
  type = string
}

variable "secrets" {
  type = object({
    SLACK_SYSTEM_BOT_TOKEN = object({
      data      = string
      accessors = list(string)
    })
    SENDGRID_API_KEY = object({
      data      = string
      accessors = list(string)
    })
    EVENTBRITE_API_KEY = object({
      data      = string
      accessors = list(string)
    })
    STRIPE_SECRET_KEY = object({
      data      = string
      accessors = list(string)
    })
    GOOGLE_MAPS_API_KEY = object({
      data      = string
      accessors = list(string)
    })
  })
}
