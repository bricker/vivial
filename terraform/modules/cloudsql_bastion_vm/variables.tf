variable "name" {
  type = string
}

variable "target_service_account" {
  type = object({
    id         = string
    account_id = string
    name       = string
    email      = string
  })
}

variable "google_sql_database_instance" {
  type = object({
    name            = string
    connection_name = string
  })
}

variable "google_compute_network" {
  type = object({
    name = string
  })
}

variable "google_compute_subnetwork" {
  type = object({
    name = string
  })
}

variable "compute_oslogin_role_name" {
  type = string
}

variable "service_account_user_role_name" {
  type = string
}

variable "accessors" {
  type = list(string)
}