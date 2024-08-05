variable "root_domain" {
  type = string
}

variable "visibility" {
  type    = string
  default = "public"
}

variable "records" {
  type = list(object({
    type = string
    subdomain = optional(string)
    datas = list(string)
  }))

  default = []
}