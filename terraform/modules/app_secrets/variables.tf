variable "secret_accessor_role_name" {
  type = string
}

variable "secrets" {
  type = object({
    EAVE_GOOGLE_OAUTH_CLIENT_CREDENTIALS_JSON_B64 = object({
      data      = string
      accessors = list(string)
    })

    SLACK_SYSTEM_BOT_TOKEN = object({
      data      = string
      accessors = list(string)
    })

    OPENAI_API_KEY = object({
      data      = string
      accessors = list(string)
    })
  })
}
