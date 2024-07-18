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