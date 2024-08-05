variable "name" {
  type = string
}

variable "service_name" {
  type = string
}

variable "namespace" {
  type = string
}

variable "iap_oauth_client_secret_name" {
  type     = string
  nullable = true
}

variable "iap_oauth_client_id" {
  type     = string
  nullable = true
}

variable "labels" {
  type    = map(string)
  default = {}
}

variable "iap_enabled" {
  type=bool
}