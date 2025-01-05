variable "location" {
  type        = string
  description = "Specify either a region or a zone. Region spreads the cluster out over all zones in the region. Zone deploys the cluster into just one zone. Zone is better for lower environments."
}

variable "authorized_networks" {
  type = map(object({
    cidr_block   = string
    display_name = string
  }))

  default = {}
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
  nullable = true
}

variable "cluster_name" {
  type = string
}

variable "docker_repository_ref" {
  type = object({
    location      = string
    repository_id = string
  })
}

variable "use_default_service_account" {
  # This was necessary because the prod cluster is using the default compute engine service account
  # but the lower environments don't, and the service account can't be replaced once the cluster is created.
  type = bool
}
