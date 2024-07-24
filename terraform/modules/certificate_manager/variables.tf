variable "certificate_map" {
  type = string
}

variable "cert_name" {
  type = string
}

variable "entry_name" {
  type = string
}

variable "hostname" {
  type = string
}

variable "domains" {
  type        = list(string)
  description = "If not given, the hostname will be used"
  nullable    = true
  default     = null
}
