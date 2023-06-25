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

# resource "google_project" "eavefyi-dev" {
#   name = "Eave Development"
#   project_id = "eavefyi-dev"
#   org_id = "482990375115"
# }

# import {
#   to = google_app_engine_application.app
#   id = "eavefyi-dev"
# }

# resource "google_app_engine_application" "app" {
#   project     = google_project.eavefyi-stg.project_id
#   location_id = "us-central"
# }