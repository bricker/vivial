# https://registry.terraform.io/providers/hashicorp/google/latest/docs


locals {
  project_id       = "eave-staging"
  region           = "us-central1"
  zone             = "us-central1-c"
  billing_account  = "013F5E-137CB0-B6AA2A"
  org_id           = "482990375115"
  eave_domain_apex = "eave.dev"

  authorized_networks = {
    "bryan-ethernet": {
      cidr_block   = "157.22.33.185/32"
      display_name = "Bryan's Home Ethernet"
    },
    "bryan-wifi": {
      cidr_block   = "157.22.33.161/32"
      display_name = "Bryan's Home Wifi"
    },
    "lana-home": {
      cidr_block   = "75.84.53.143/32"
      display_name = "Lana's Home Network"
    },
    "liam-home": {
      cidr_block   = "76.146.71.81/32"
      display_name = "Liam's Home Network"
    }
  }

  # These are auto-created with the project
  default_network_id = "projects/${local.project_id}/global/networks/default"
  default_subnetwork_id = "projects/${local.project_id}/${local.region}/subnetworks/default"
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
  source          = "../../modules/gcp/project"
  project_id = local.project_id
  org_id          = local.org_id
}

module "gcp_nat" {
  source = "../../modules/gcp/nat"
  project_id = local.project_id
  region = local.region
  network_id = local.default_network_id
}

module "gcp_gke" {
  source     = "../../modules/gcp/gke"
  project_id = local.project_id
  region     = local.region
  network_id = local.default_network_id
  subnetwork_id = local.default_subnetwork_id
  authorized_networks = local.authorized_networks

  google_service_accounts = {
    "gsa-metabase-01": {
      bound_ksa = "metabase/ksa-metabase-01"
    },
    "gsa-eave-core": {
      bound_ksa = "eave/ksa-eave-core"
    }
  }

  roles = {
    "roles/cloudsql.client": {
      google_service_accounts = [
        "gsa-metabase-01",
        "gsa-eave-core",
      ]
    },
    "roles/logging.logWriter": {
      google_service_accounts = [
        "gsa-metabase-01",
        "gsa-eave-core",
      ]
    },
  }
}

# module "cloudsql_metabase" {
#   source = "../../modules/gcp/cloud_sql"
#   project_id = local.project_id
#   region = local.region
#   instance_name = "metabase"
#   instance_tier = ""
#   instance_disk_type = ""
#   instance_disk_size = ""
#   instance_backup_enabled = ""
#   instance_zone = ""
#   project_id = ""
# }

# module "cloudsql_eave_core" {
#   source = "../../modules/gcp/cloud_sql"
#   project_id = local.project_id
# }

# module "metabase_resources" {
#   source = "../../modules/gcp/metabase_resources"
#   project_id = local.project_id
#   metabase_instances = [
#     "metabase-01" # TODO: This needs to be more dynamic; currently we'll have to update this list for each new customer.
#   ]
# }

# module "gcp_iam" {
#   source     = "../../modules/gcp/iam"
#   project_id = local.project_id
# }

# module "gcp_bigquery" {
#   source     = "../../modules/gcp/bigquery"
#   project_id = local.project_id
#   region     = local.region
# }
