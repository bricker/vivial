locals {
  billing_account = "013F5E-137CB0-B6AA2A"
  org_id          = "482990375115"
  project_id      = "eave-production"
  project_number  = "287112967940"
  default_region  = "us-central1"
  default_zone    = "us-central1-a"

  environment     = "PROD"
  dns_domain      = "vivialapp.com"
  resource_domain = "eave.fyi" # This is used for Storage buckets and stuff, because our public domain changed but we couldn't delete all of our resources.

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

  managed_projects = toset([
    "eave-production",
    "eave-staging",
    "eave-develop",
  ])

  STRIPE_ENVIRONMENT = "live"
  EAVE_ENV = "production"
}
