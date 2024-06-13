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

variable "INTERNAL_EAVE_CREDENTIALS" {
  type = object({
    SERVER_CREDENTIALS = string,
    CLIENT_ID          = string,
  })
  sensitive = true
}

variable "IAP_OAUTH_CLIENT_CREDENTIALS" {
  type = object({
    client_id     = string
    client_secret = string
  })
  sensitive = true
}