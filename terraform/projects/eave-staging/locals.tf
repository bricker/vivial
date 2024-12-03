locals {
  project_id     = "eave-staging"
  project_number = "264481035543"
  default_region = "us-central1"
  default_zone   = "us-central1-a"

  environment     = "STG"
  dns_domain      = "eave.dev"
  resource_domain = "eave.dev"

  www_public_domain_prefix = "www"
  api_public_domain_prefix = "api"

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

  # These are not considered sensitive values
  SEGMENT_CORE_API_WRITE_KEY = "uUjBMbm9CcTL9XV1Rf6S9xGpLnvtCObZ"
  SEGMENT_WEBSITE_WRITE_KEY  = "dO1quf6odO8UQ5lLiJPHu0SFjy6OImu1"
  STRIPE_PUBLISHABLE_KEY     = "pk_test_51NXpyaDQEmxo4go9FNJWSszhjShiPJNSPF8TNidSdSDttvVPnpHOAmkFzPM8pfywwwSngOXxXWfDGvbjz2sevFO900ACLz7Tqm"
}