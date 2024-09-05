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

variable "root_domain" {
  type = string
}

variable "network_name" {
  type = string
}

variable "subnetwork_self_link" {
  type     = string
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