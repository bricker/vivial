variable "application_title" {
  type=string
}

variable "gateways" {
  type = map(object({
    name = string
  }))
}

variable "dns_domain" {
  type=string
}
