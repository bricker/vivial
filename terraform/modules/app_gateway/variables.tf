variable "service_name" {
  type = string
}

variable "namespace" {
  type = string
}

variable "google_certificate_manager_certificate_map" {
  type = object({
    name = string
  })
}

variable "global_address_names" {
  type = set(string)
}

variable "google_compute_ssl_policy" {
  type = object({
    name = string
  })
}
