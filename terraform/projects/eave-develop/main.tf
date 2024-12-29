# https://registry.terraform.io/providers/hashicorp/google/latest/docs

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.10"
    }
  }

  backend "gcs" {
    bucket = "terraform.eave-develop.eave.fyi" # project ID hardcoded because changing it would break TF state
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
