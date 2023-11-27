# https://registry.terraform.io/providers/hashicorp/google/latest/docs

variable "EAVE_GITHUB_APP_CRON_SECRET" {
  type      = string
  sensitive = true
}

variable "GCP_MONITORING_SLACK_AUTH_TOKEN" {
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

module "gcp_cloud_tasks" {
  source     = "../modules/gcp/cloud_tasks"
  project_id = local.project_id
  region     = local.region
}

module "gcp_cloud_scheduler" {
  source             = "../modules/gcp/cloud_scheduler"
  project_id         = local.project_id
  region             = local.region
  cron_shared_secret = var.EAVE_GITHUB_APP_CRON_SECRET
}

module "gcp_monitoring" {
  source           = "../modules/gcp/monitoring"
  project_id       = local.project_id
  region           = local.region
  eave_domain_apex = local.eave_domain_apex
  slack_auth_token = var.GCP_MONITORING_SLACK_AUTH_TOKEN
  addl_notification_channels = [
    "projects/eave-production/notificationChannels/18048082649449908319" // bryan mobile... unable to import into terraform
  ]
}

# module "gcp_memorystore" {
#   source     = "../modules/gcp/memorystore"
#   project_id = local.project_id
#   region     = local.region
#   notification_channels = [
#     module.gcp_monitoring.slack_notification_channel_name,
#     "projects/eave-production/notificationChannels/18048082649449908319" // bryan mobile... unable to import into terraform
#   ]
# }
