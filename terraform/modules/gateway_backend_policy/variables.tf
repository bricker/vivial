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
  type=bool
}

variable "iap_client_kube_secret_name" {
  type     = string
  nullable = true
}

variable "iap_client_ref" {
  type = object({
    brand=string
    client_id=string
  })
  nullable = true
}

variable "labels" {
  type    = map(string)
  default = {}
}
