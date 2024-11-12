variable "secret_accessor_role_name" {
  type = string
}

variable "secrets" {
  type = object({
    SLACK_SYSTEM_BOT_TOKEN = object({
      data      = string
      accessors = list(string)
    })

    OPENAI_API_KEY = object({
      data      = string
      accessors = list(string)
    })

    GOOGLE_PLACES_API_KEY = object({
      data      = string
      accessors = list(string)
    })

    EVENTBRITE_API_KEY = object({
      data      = string
      accessors = list(string)
    })
  })
}
