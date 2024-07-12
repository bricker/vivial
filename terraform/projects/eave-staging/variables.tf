variable "MB_SHARED_SECRETS" {
  type      = map(string)
  sensitive = true
}

variable "MB_INSTANCE_SECRETS" {
  type      = map(map(string))
  sensitive = true
}

variable "PLAYGROUND_TODOAPP_EAVE_CREDENTIALS" {
  type = object({
    SERVER_CREDENTIALS = string,
    CLIENT_ID          = string,
  })
  sensitive = true
}

variable "PLAYGROUND_QUIZAPP_EAVE_CREDENTIALS" {
  type = object({
    SERVER_CREDENTIALS = string,
    CLIENT_ID          = string,
  })
  sensitive = true
}

variable "INTERNAL_EAVE_CREDENTIALS" {
  type = object({
    SERVER_CREDENTIALS = string,
    CLIENT_ID          = string,
  })
  sensitive = true
}

variable "IAP_OAUTH_CLIENT_ID" {
  type = string
}

variable "IAP_OAUTH_CLIENT_SECRET" {
  type = string
  sensitive = true
}

variable "OPENAI_API_KEY" {
  type      = string
  sensitive = true
}
