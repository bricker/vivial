variable "service_name" {
  type = string
}

variable "namespace" {
  type = string
}

variable "certificate_map_name" {
  type = string
}

variable "global_address_names" {
  type = list(string)
}

variable "ssl_policy_name" {
  type = string
}

variable "labels" {
  type    = map(string)
  default = {}
}
