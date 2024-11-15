locals {
  billing_account = "013F5E-137CB0-B6AA2A"
  org_id          = "482990375115"
  project_id      = "eave-production"
  project_number  = "287112967940"
  default_region  = "us-central1"
  default_zone    = "us-central1-a"

  environment = "PROD"
  root_domain = "eave.fyi"

  eave_slack_signups_channel_id = "C04HH2N08LD" # #sign-ups in eave slack

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

  managed_projects = toset([
    "eave-production",
    "eave-staging",
    "eave-develop",
  ])

  # These are not considered sensitive values
  SEGMENT_WEBSITE_WRITE_KEY  = "GcB5ShHbFcZZKIGTlvanJerSyKp9yJNv"
  SEGMENT_CORE_API_WRITE_KEY = "cVBM36ZvqJV2gagtnOT60fTNn1Q5P5na"
}