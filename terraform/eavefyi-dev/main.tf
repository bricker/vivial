# https://registry.terraform.io/providers/hashicorp/google/latest/docs

# variable "EAVE_GITHUB_APP_CRON_SECRET" {
#   type      = string
#   sensitive = true
# }

locals {
  project_id       = "eavefyi-dev"
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

# module "gcp_cloud_tasks" {
#   source     = "../modules/gcp/cloud_tasks"
#   project_id = local.project_id
#   region     = local.region
# }

# module "gcp_cloud_scheduler" {
#   source             = "../modules/gcp/cloud_scheduler"
#   project_id         = local.project_id
#   region             = local.region
#   cron_shared_secret = var.EAVE_GITHUB_APP_CRON_SECRET
# }

# module "gcp_secret_manager" {
#   source = "../modules/gcp/secret_manager"
# }

# module "gcp_gke" {
#   source     = "../modules/gcp/gke"
#   project_id = local.project_id
#   region     = local.region
# }

# module "gcp_iam" {
#   source     = "../modules/gcp/iam"
#   project_id = local.project_id
# }

module "gcp_bigquery" {
  source     = "../modules/gcp/bigquery"
  project_id = local.project_id
  region     = local.region
}

resource "google_project_iam_binding" "bigquery_data_owner" {
  project = local.project_id
  role    = "roles/bigquery.dataOwner"

  members = [
    "domain:eave.fyi"
  ]
}
