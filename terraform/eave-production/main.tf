# https://registry.terraform.io/providers/hashicorp/google/latest/docs

variable "cron_shared_secret" {
  type      = string
  sensitive = true
}

locals {
  project_id       = "eave-production"
  region           = "us-central1"
  zone             = "us-central1-c"
  billing_account  = "013F5E-137CB0-B6AA2A"
  org_id           = "482990375115"
  eave_domain_apex = "eave.fyi"
}

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.51.0"
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

module "gcp_cloud_tasks" {
  source     = "../modules/gcp/cloud_tasks"
  project_id = local.project_id
  region     = local.region
}

module "gcp_cloud_scheduler" {
  source             = "../modules/gcp/cloud_scheduler"
  project_id         = local.project_id
  region             = local.region
  cron_shared_secret = var.cron_shared_secret
}

module "gcp_memorystore" {
  source     = "../modules/gcp/memorystore"
  project_id = local.project_id
  region     = local.region
}

module "gcp_monitoring" {
  source           = "../modules/gcp/monitoring"
  project_id       = local.project_id
  region           = local.region
  eave_domain_apex = local.eave_domain_apex
}

module "gcp_pubsub" {
  source     = "../modules/gcp/pubsub"
  project_id = local.project_id
  region     = local.region
}
