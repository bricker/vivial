variable "metabase_instances" {
  type = list(string)
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

variable "MB_SHARED_SECRETS" {
  type = any
  sensitive = true
}

variable "MB_INSTANCE_SECRETS" {
  type = any
  sensitive = true
}
