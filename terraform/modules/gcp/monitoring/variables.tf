variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "addl_notification_channels" {
  type = list(string)
  default = []
}