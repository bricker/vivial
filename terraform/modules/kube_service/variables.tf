variable "namespace" {
  type = string
}

variable "service_name" {
  type = string
}

variable "service_port" {
  type = object({
    name   = string
    number = number
  })
}

variable "app_name" {
  type = string
}
variable "app_port" {
  type = object({
    name   = string
    number = number
  })
}

variable "iap_oauth_client_kube_secret_name" {
  type = string
}

variable "iap_oauth_client_id" {
  type = string
}

variable "iap_enabled" {
  type = bool
}