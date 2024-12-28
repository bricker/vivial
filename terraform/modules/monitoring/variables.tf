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
    service         = string
    name            = string
    enabled         = bool
    severity        = string
    host            = string
    path            = string
    contains_string = optional(string)
    matches_json_path = optional(object({
      content   = string
      json_path = string
    }))
    authenticated = bool
  }))
}
