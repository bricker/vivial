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
