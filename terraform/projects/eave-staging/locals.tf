locals {
  billing_account = "013F5E-137CB0-B6AA2A"
  org_id          = "482990375115"
  project_id = "eave-staging"
  default_region      = "us-central1"
  default_zone        = "us-central1-a"

  environment = "STG"
  root_domain = "eave.dev"

  authorized_networks = {
    "bryan-ethernet" : {
      cidr_block   = "157.22.33.185/32"
      display_name = "Bryan's Home Ethernet"
    },
    "bryan-wifi" : {
      cidr_block   = "157.22.33.161/32"
      display_name = "Bryan's Home Wifi"
    },
    # "lana-home" : {
    #   cidr_block   = "75.84.53.143/32"
    #   display_name = "Lana's Home Network"
    # },
    "liam-home" : {
      cidr_block   = "73.35.152.53/32"
      display_name = "Liam's Home Network"
    },
    "cabin-wifi" : {
      cidr_block   = "23.241.98.185/32"
      display_name = "Bryan's Cabin Wifi"
    },
  }
}