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

variable "compute_vm_accessor_role_name" {
  type = string
}

variable "accessors" {
  type = list(string)
}