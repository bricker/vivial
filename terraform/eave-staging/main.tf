# https://registry.terraform.io/providers/hashicorp/google/latest/docs


locals {
  project_id       = "eave-staging"
  region           = "us-central1"
  zone             = "us-central1-c"
  billing_account  = "013F5E-137CB0-B6AA2A"
  org_id           = "482990375115"
  eave_domain_apex = "eave.dev"
}

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = local.project_id
  region  = local.region
  zone    = local.zone
}

module "gcp_project" {
  source          = "../modules/gcp/project"
  project_id      = local.project_id
  billing_account = local.billing_account
  org_id          = local.org_id
}

module "gcp_networking" {
  source = "../modules/gcp/networking"
  project_id = local.project_id
  region = local.region
}

module "gcp_gke" {
  source     = "../modules/gcp/gke"
  project_id = local.project_id
  region     = local.region
  network = module.gcp_networking.default_network.name
}

module "metabase_resources" {
  source = "../modules/gcp/metabase_resources"
  project_id = local.project_id
  metabase_instances = [
    "metabase-01" # TODO: This needs to be more dynamic; currently we'll have to update this list for each new customer.
  ]
}

# module "gcp_iam" {
#   source     = "../modules/gcp/iam"
#   project_id = local.project_id
# }

# module "gcp_bigquery" {
#   source     = "../modules/gcp/bigquery"
#   project_id = local.project_id
#   region     = local.region
# }
