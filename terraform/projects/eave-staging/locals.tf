locals {
  project_id      = "eave-staging"
  region          = "us-central1"
  zone            = "us-central1-a"
  billing_account = "013F5E-137CB0-B6AA2A"
  org_id          = "482990375115"
  root_domain     = "eave.dev"
  environment     = "STG"

  authorized_networks = {
    "bryan-ethernet" : {
      cidr_block   = "157.22.33.185/32"
      display_name = "Bryan's Home Ethernet"
    },
    "bryan-wifi" : {
      cidr_block   = "157.22.33.161/32"
      display_name = "Bryan's Home Wifi"
    },
    "lana-home" : {
      cidr_block   = "75.84.53.143/32"
      display_name = "Lana's Home Network"
    },
    "liam-home" : {
      cidr_block   = "76.146.71.81/32"
      display_name = "Liam's Home Network"
    }
  }

  # # These are auto-created with the project
  # default_network_id = "projects/${local.project_id}/global/networks/default"
  # default_subnetwork_id = "projects/${local.project_id}/${local.region}/subnetworks/default"

  metabase_instances = toset([
    "dev"
  ])
}