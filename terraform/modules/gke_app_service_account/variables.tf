variable "kubernetes_service" {
  type = object({
    name = string
  })
}

variable "kube_namespace_name" {
  type = string
}
