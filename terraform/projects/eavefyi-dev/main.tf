# https://registry.terraform.io/providers/hashicorp/google/latest/docs


locals {
  project_id       = "eavefyi-dev"
  region           = "us-central1"
  zone             = "us-central1-c"
  billing_account  = "013F5E-137CB0-B6AA2A"
  org_id           = "482990375115"
  base_domain = "eave.run"
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
  source          = "../../modules/project"
  project_id      = local.project_id
  billing_account = local.billing_account
  org_id          = local.org_id
}

# module "gcp_cloud_tasks" {
#   source     = "../../modules/cloud_tasks"
#   project_id = local.project_id
#   region     = local.region
# }

# module "gcp_cloud_scheduler" {
#   source             = "../../modules/cloud_scheduler"
#   project_id         = local.project_id
#   region             = local.region
#   cron_shared_secret = var.EAVE_GITHUB_APP_CRON_SECRET
# }

# module "gcp_secret_manager" {
#   source = "../../modules/secret_manager"
# }

module "gcp_gke" {
  source     = "../../modules/gke"
  project_id = local.project_id
  region     = local.region
}

module "gcp_iam" {
  source     = "../../modules/iam"
  project_id = local.project_id
}

# resource "google_project_iam_binding" "bigquery_data_owner" {
#   project = local.project_id
#   role    = "roles/bigquery.dataOwner"

#   members = [
#     "domain:eave.fyi"
#   ]
# }

# module "gcp_bigquery" {
#   source     = "../../modules/bigquery"
#   project_id = local.project_id
#   region     = local.region
# }
