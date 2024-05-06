# https://registry.terraform.io/providers/hashicorp/google/latest/docs


locals {
  project = {
    id      = "eave-staging"
    region          = "us-central1"
    zone            = "us-central1-a"
    environment     = "STG"
    root_domain     = "eave.dev"

    preset_development = true
    preset_production = false
  }

  billing_account = "013F5E-137CB0-B6AA2A"
  org_id          = "482990375115"

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
}

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
  project=local.project
  org_id          = local.org_id
  billing_account = local.billing_account
}

module "tfstate" {
  source     = "../../modules/tfstate"
  project = local.project
}

module "docker_registry" {
  source = "../../modules/docker_registry"
}

module "nat" {
  source     = "../../modules/nat"
}

module "dns_zone_base_domain" {
  source = "../../modules/dns_zone"
  project = local.project
}

module "cloudsql_instance" {
  source              = "../../modules/cloudsql_instance"
  project = local.project
  instance_name = "eave-pg-core"
}
