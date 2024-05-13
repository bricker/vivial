# https://registry.terraform.io/providers/hashicorp/google/latest/docs

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.0.1"
    }
  }

  backend "gcs" {
    bucket = "tfstate.eave-staging.eave.fyi"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = local.project.id
  region  = local.project.region
  zone    = local.project.zone
}

module "gcp_project" {
  source          = "../../modules/project"
  project         = local.project
  org_id          = local.org_id
  billing_account = local.billing_account
}

module "tfstate" {
  source  = "../../modules/tfstate"
  project = local.project
}

module "docker_registry" {
  source = "../../modules/docker_registry"
}

module "nat" {
  source = "../../modules/nat"
}

module "dns_zone_base_domain" {
  source      = "../../modules/dns_zone"
  root_domain = local.project.root_domain
}

module "cloudsql_eave_core" {
  source        = "../../modules/cloudsql_instance"
  project       = local.project
  instance_name = "eave-pg-core"
}

module "ssl_policy" {
  source = "../../modules/ssl_policy"
}