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