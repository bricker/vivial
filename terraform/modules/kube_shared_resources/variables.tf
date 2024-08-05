variable "iap_client_ref" {
  type = object({
    brand=string
    client_id=string
  })
}

variable "root_domain" {
  type=string
}