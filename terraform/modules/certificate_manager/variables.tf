variable "google_certificate_manager_certificate_map" {
  type = object({
    name = string
  })
}

variable "cert_name" {
  type = string
}

variable "entry_name" {
  type = string
}

variable "hostname" {
  type = string
}

variable "use_dns_authorization" {
  type    = bool
  default = false
}
