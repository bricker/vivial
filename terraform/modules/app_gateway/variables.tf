variable "kubernetes_service" {
  type = object({
    name = string
  })
}

variable "kubernetes_namespace_name" {
  type = string
}

variable "google_certificate_manager_certificate_map" {
  type = object({
    name = string
  })
}

variable "google_compute_global_addresses" {
  type = list(object({
    name = string
  }))
}

variable "google_compute_ssl_policy" {
  type = object({
    name = string
  })
}
