variable "project" {
  type = object({
    region            = string
    zone              = string
    preset_production = bool
  })
}

variable "instance_name" {
  type = string
}

variable "network_id" {
  type = string
}