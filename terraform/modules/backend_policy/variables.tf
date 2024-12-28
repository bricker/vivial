variable "name" {
  type = string
}

variable "service_name" {
  type = string
}

variable "namespace" {
  type = string
}

variable "iap_enabled" {
  type = bool
}

variable "iap_oauth_client_kube_secret_name" {
  type     = string
  nullable = true
}

variable "iap_oauth_client_id" {
  type     = string
  nullable = true
}
