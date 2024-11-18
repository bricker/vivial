variable "iap_oauth_client_secret" {
  type      = string
  sensitive = true
}

variable "dns_domain" {
  type = string
}

variable "eave_slack_signups_channel_id" {
  type = string
}

variable "www_public_domain_prefix" {
  type    = string
  default = "www"
}

variable "api_public_domain_prefix" {
  type    = string
  default = "api"
}
