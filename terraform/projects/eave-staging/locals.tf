locals {
  project_id     = "eave-staging"
  project_number = "264481035543"
  default_region = "us-central1"
  default_zone   = "us-central1-a"

  dns_domain      = "eave.dev"
  resource_domain = "eave.dev"

  www_public_domain_prefix   = "www"
  api_public_domain_prefix   = "api"
  admin_public_domain_prefix = "admin"

  authorized_networks = {
    "bryan-wifi" : {
      cidr_block   = "75.83.177.2/32"
      display_name = "Bryan's Home Wifi"
    },
    "liam-home" : {
      cidr_block   = "73.35.152.53/32"
      display_name = "Liam's Home Network"
    },
  }

  STRIPE_ENVIRONMENT = "test"
  EAVE_ENV           = "staging"
}
