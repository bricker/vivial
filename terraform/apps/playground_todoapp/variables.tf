variable "dns_zone_name" {
  type = string
}

variable "docker_repository_ref" {
  type = object({
    location = string
    repository_id = string
  })
}

variable "ssl_policy_name" {
  type = string
}

variable "certificate_map_name" {
  type = string
}

variable "kube_namespace_name" {
  type = string
}

variable "shared_config_map_name" {
  type = string
}

variable "cloudsql_instance_name" {
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
  default = "debug"
}


variable "EAVE_CREDENTIALS" {
  type = object({
    SERVER_CREDENTIALS = string,
    CLIENT_ID          = string,
  })
  sensitive = true
}

variable "iap_oauth_client_id" {
  type=string
}

variable "iap_oauth_client_kube_secret_name" {
  type = string
}