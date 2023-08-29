# https://registry.terraform.io/providers/hashicorp/google/latest/docs

terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "4.51.0"
    }
  }
}

provider "google" {
  project = "eavefyi-dev"
  region  = "us-central1"
  zone    = "us-central1-c"
}

module "project" {
  source = "../modules/project"

}

module "cloud-tasks" {
  source = "../modules/cloud-tasks"
  project_id = local.project_id
  region = local.region
}