variable "application_title" {
  type = string
}

variable "backend_services" {
  type = map(object({
    name = string
  }))
}

variable "dns_domain" {
  type = string
}
