variable "metabase_instance_id" {
  type = string
}

variable "team_id" {
  type = string
}

variable "project" {
  type = object({
    id = string
    region = string
    root_domain = string
  })
}

variable "cloudsql_instance_name" {
  type=string
}

variable "kube_namespace_name" {
  type=string
}

variable "shared_metabase_secret_name" {
  type = string
}

variable "shared_metabase_config_map_name" {
  type = string
}

variable "iap_oauth_client_credentials_secret_name" {
  type = string
}

variable "MB_INSTANCE_SECRETS" {
  type = any
  sensitive = true
}

variable "dns_zone" {
  type = object({
    name     = string
    dns_name = string
  })
}