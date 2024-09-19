variable "name" {
  type = string
}

variable "target_service_account_id" {
  type = string
}

variable "cloudsql_instance_name" {
  type = string
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

variable "accessors" {
  type = list(string)
}