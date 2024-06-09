variable "project" {
  type = object({
    id          = string
    region      = string
    root_domain = string
  })
}

variable "release_version" {
  type = string
}

variable "release_date" {
  type = string
}

variable "shared_config_map_name" {
  type = string
}

variable "LOG_LEVEL" {
  type    = string
  default = "debug"
}

variable "dns_zone" {
  type = object({
    name     = string
    dns_name = string
  })
}

variable "docker_repository" {
  type = object({
    location      = string
    project       = string
    repository_id = string
  })
}

variable "ssl_policy_name" {
  type = string
}

variable "certificate_map_name" {
  type = string
}

variable "cdn_base_url" {
  type = string
}

variable "kube_namespace_name" {
  type = string
}

variable "EAVE_CREDENTIALS" {
  type = object({
    SERVER_CREDENTIALS = string,
    CLIENT_ID          = string,
  })
  sensitive = true
}