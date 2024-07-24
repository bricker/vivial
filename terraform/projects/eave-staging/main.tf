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

provider "kubernetes" {
  host                   = "https://${module.gke.cluster.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(module.gke.cluster.master_auth[0].cluster_ca_certificate)

  # config_path = "~/.kube/config"
  # config_context = "eave-staging"

  ignore_annotations = [
    "^autopilot\\.gke\\.io\\/.*",
    "^cloud\\.google\\.com\\/.*",
  ]
}
