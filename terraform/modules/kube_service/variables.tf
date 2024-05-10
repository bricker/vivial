variable "namespace" {
  type=string
}

variable "service_name" {
  type=string
}

variable "service_port" {
  type=object({
    name = string
    number = number
  })
}

variable "app_port" {
  type=object({
    name = string
    number = number
  })
}