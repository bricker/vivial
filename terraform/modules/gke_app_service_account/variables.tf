variable "kube_service_name" {
  type = string
}

variable "kube_namespace_name" {
  type = string
}

variable "project" {
  type = object({
    id = string
  })
}