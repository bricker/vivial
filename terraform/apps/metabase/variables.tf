variable "metabase_instances" {
  type = list(object({
    metabase_instance_id = string
    team_id = string
  }))
}

variable "project" {
  type = object({
    id = string
    region = string
    root_domain = string
  })
}

variable "kube_namespace_name" {
  type = string
}

variable "cloudsql_instance_name" {
  type=string
}

variable "ssl_policy_name" {
  type=string
}

variable "MB_SHARED_SECRETS" {
  type = any
  sensitive = true
}

variable "MB_INSTANCE_SECRETS" {
  type = any
  sensitive = true
}

variable "IAP_OAUTH_CLIENT_CREDENTIALS" {
  type = object({
    client_id=string
    client_secret=string
  })
}

variable "dns_zone" {
  type = object({
    name     = string
    dns_name = string
  })
}