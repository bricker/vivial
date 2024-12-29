# https://registry.terraform.io/providers/hashicorp/google/latest/docs

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.10"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.0.1"
    }
  }

  backend "gcs" {
    bucket = "terraform.eave-production.eave.fyi" # project ID hardcoded because changing it would break TF state
    prefix = "state"
  }
}

provider "google" {
  project = local.project_id
  region  = local.default_region
  zone    = local.default_zone

  # The following are necessary when using certain APIs for a complicated reason related to ADC.
  # In our case, we're using the orgpolicy API which has this issue.
  # See:
  # - https://github.com/hashicorp/terraform-provider-google/issues/1538#issuecomment-392385194
  # - https://github.com/hashicorp/terraform-provider-google/issues/17998
  billing_project       = local.project_id
  user_project_override = true
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
