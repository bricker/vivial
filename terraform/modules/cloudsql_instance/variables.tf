variable "instance_name" {
  type = string
}

variable "google_compute_network" {
  type = object({
    id = string
  })
}

variable "global_address_name" {
  type = string
}

variable "cloudsql_user_role_members" {
  type = list(string)
}

variable "preset" {
  type = string

  validation {
    condition     = contains(["PROD", "NONPROD"], var.preset)
    error_message = "preset must be one of PROD, NONPROD"
  }
}

variable "enable_backups" {
  type = bool
}

variable "disk_size_gb" {
  type = number
}
