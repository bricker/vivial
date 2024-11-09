variable "environment" {
  description = "Allowed values: DEV, STG, PROD"
  type        = string
  default     = "DEV"

  validation {
    condition     = contains(["DEV", "STG", "PROD"], var.environment)
    error_message = "Allowed values: DEV, STG, PROD"
  }
}

variable "dns_zone_name" {
  type = string
}

variable "docker_repository_ref" {
  type = object({
    location      = string
    repository_id = string
  })
}

variable "ssl_policy_name" {
  type = string
}

variable "certificate_map_name" {
  type = string
}

variable "kube_namespace_name" {
  type = string
}

variable "shared_config_map_name" {
  type = string
}

variable "cloudsql_instance_name" {
  type = string
}

variable "release_version" {
  type = string
}

variable "LOG_LEVEL" {
  type    = string
  default = "debug"
}

variable "impersonator_role_name" {
  type = string
}

variable "impersonators" {
  type    = list(string)
  default = []
}

variable "network_name" {
  type = string
}
variable "subnetwork_self_link" {
  type = string
}
variable "compute_oslogin_role_name" {
  type = string
}
variable "service_account_user_role_name" {
  type = string
}
variable "bastion_accessors" {
  type    = list(string)
  default = []
}

variable "SEGMENT_CORE_API_WRITE_KEY" {
  type = string
  // value can be obtained from target Core API source https://app.segment.com/vivial/sources
}
