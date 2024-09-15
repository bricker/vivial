variable "instance_name" {
  type = string
}

variable "network_name" {
  type = string
}

variable "global_address_name" {
  type = string
}

variable "environment" {
  description = "Allowed values: DEV, STG, PROD"
  type        = string
  default     = "DEV"

  validation {
    condition     = contains(["DEV", "STG", "PROD"], var.environment)
    error_message = "Allowed values: DEV, STG, PROD"
  }
}

variable "cloudsql_user_role_name" {
  type=string
}

variable "cloudsql_user_role_members" {
  type=list(string)
}