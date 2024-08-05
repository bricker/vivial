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
    bucket = "tfstate.eave-staging.eave.fyi" # project ID hardcoded because changing it would break TF state
    prefix = "terraform/state"
  }
}

provider "google" {
  project = local.project_id
  region  = local.default_region
  zone    = local.default_zone
}

provider "google-beta" {
  project = local.project_id
  region  = local.default_region
  zone    = local.default_zone
}

provider "kubernetes" {
  host                   = "https://${module.gke_primary.cluster.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(module.gke_primary.cluster.master_auth[0].cluster_ca_certificate)

  # config_path = "~/.kube/config"
  # config_context = "eave-staging"

  ignore_annotations = [
    "^autopilot\\.gke\\.io\\/.*",
    "^cloud\\.google\\.com\\/.*",
  ]
}
