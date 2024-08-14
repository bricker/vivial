variable "secret_id" {
  type = string
}

variable "secret_data" {
  type      = string
  sensitive = true
}

variable "accessors" {
  type=list(string)
}

variable "secret_accessor_role_id" {
  type = string
}