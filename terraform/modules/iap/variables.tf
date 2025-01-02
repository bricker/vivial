variable "application_title" {
  type=string
}

variable "gateways" {
  type = map(string)
}

variable "dns_domain" {
  type=string
}