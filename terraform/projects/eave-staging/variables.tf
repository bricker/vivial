variable "MB_SHARED_SECRETS" {
  type = any
  sensitive = true
}

variable "MB_INSTANCE_SECRETS" {
  type = any
  sensitive = true
}

variable "PLAYGROUND_TODOAPP_EAVE_CREDENTIALS" {
  type=string
  sensitive=true
}

variable "IAP_OAUTH_CLIENT_CREDENTIALS" {
  type = object({
    client_id=string
    client_secret=string
  })
}