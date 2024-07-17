variable "project" {
  type = object({
    root_domain=string
  })
}

variable "dns_zone" {
  type = object({
    name     = string
    dns_name = string
  })
}

variable "certificate_map" {
  type = object({
    id = string
    name = string
  })
}