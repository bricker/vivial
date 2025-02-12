variable "public_domain_prefix" {
  type    = string
  default = "admin"
}

variable "google_dns_managed_zone" {
  type = object({
    name     = string
    dns_name = string
  })
}

variable "google_compute_ssl_policy" {
  type = object({
    name = string
  })
}

variable "google_certificate_manager_certificate_map" {
  type = object({
    id   = string
    name = string
  })
}

variable "docker_repository_ref" {
  type = object({
    location      = string
    repository_id = string
  })
}

variable "kube_namespace_name" {
  type = string
}

variable "shared_config_map_name" {
  type = string
}

variable "cdn_base_url" {
  type = string
}

variable "release_version" {
  type = string
}

variable "LOG_LEVEL" {
  type    = string
  default = "info"
}

variable "iap_jwt_aud" {
  type = string
}
