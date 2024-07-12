variable "project" {
  type = object({
    id          = string
    root_domain = string
  })
}

variable "iap_oauth_client_secret" {
  type      = string
  sensitive = true
}