variable "base_roles" {
  type    = set(string)
  default = []
}

variable "role_id" {
  type = string
}

variable "title" {
  type = string
}

variable "description" {
  type     = string
  nullable = true
  default  = null
}
