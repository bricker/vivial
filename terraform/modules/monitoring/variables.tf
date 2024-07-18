variable "project" {
  type = object({
    id = string
    root_domain = string
    region = string
  })
}

variable "addl_notification_channels" {
  type    = list(string)
  default = []
}

variable "slack_auth_token" {
  type      = string
  sensitive = true
}