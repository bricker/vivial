variable "google_compute_network" {
  type=object({
    id = string
  })
}

variable "redis_user_role_members" {
  type=list(string)
}
