variable "iap_oauth_client_secret" {
  type      = string
  sensitive = true
}

variable "root_domain" {
  type = string
}

variable "eave_slack_signups_channel_id" {
  type=string
}