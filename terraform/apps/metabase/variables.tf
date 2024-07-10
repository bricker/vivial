variable "metabase_instances" {
  type = map(object({
    metabase_instance_id = string
    team_id              = string
  }))
}

variable "project" {
  type = object({
    id          = string
    region      = string
    root_domain = string
  })
}

variable "kube_namespace_name" {
  type = string
}

variable "cloudsql_instance_name" {
  type = string
}

variable "ssl_policy_name" {
  type = string
}

variable "certificate_map_name" {
  type = string
}

variable "MB_SHARED_SECRETS" {
  type      = map(string)
  sensitive = true
}

variable "MB_INSTANCE_SECRETS" {
  type      = map(map(string))
  sensitive = true
}

variable "IAP_OAUTH_CLIENT_CREDENTIALS" {
  type = object({
    client_id     = string
    client_secret = string
  })
  sensitive = true
}

variable "dns_zone" {
  type = object({
    name     = string
    dns_name = string
  })
}

variable "iap_oauth_client_secret_name" {
  type = string
}