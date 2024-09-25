locals {
  billing_account = "013F5E-137CB0-B6AA2A"
  org_id          = "482990375115"
  project_id      = "eave-staging"
  project_number      = "264481035543"
  default_region  = "us-central1"
  default_zone    = "us-central1-a"

  environment = "STG"
  root_domain = "eave.dev"

  eave_slack_signups_channel_id = "C04GDPU3B5Z" # #bot-testing in eave slack

  authorized_networks = {
    "bryan-wifi" : {
      cidr_block   = "75.83.177.78/32"
      display_name = "Bryan's Home Wifi"
    },
    "liam-home" : {
      cidr_block   = "73.35.152.53/32"
      display_name = "Liam's Home Network"
    },
  }
}