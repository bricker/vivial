variable "addl_notification_channels" {
  type    = list(string)
  default = []
}

variable "slack_auth_token" {
  type      = string
  sensitive = true
}

variable "uptime_checks" {
  type = list(object({
    service=string
    name = string
    host = string
    path = string
    severity = string
  }))
}
