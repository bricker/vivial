# https://registry.terraform.io/providers/hashicorp/google/latest/docs

variable "METABASE_UI_BIGQUERY_ACCESSOR_GSA_KEY_JSON_B64" {
  type=string
  sensitive=true
}

variable "RELEASE" {
  type=object({
    core_api=object({
      version=string
      release_date=string
    })
    dashboard=object({
      version=string
      release_date=string
    })
    playground_todoapp=object({
      version=string
      release_date=string
    })
  })
}

locals {
  project_id      = "eave-staging"
  region          = "us-central1"
  zone            = "us-central1-a"
  billing_account = "013F5E-137CB0-B6AA2A"
  org_id          = "482990375115"
  root_domain     = "eave.dev"
  environment     = "STG"

  authorized_networks = {
    "bryan-ethernet" : {
      cidr_block   = "157.22.33.185/32"
      display_name = "Bryan's Home Ethernet"
    },
    "bryan-wifi" : {
      cidr_block   = "157.22.33.161/32"
      display_name = "Bryan's Home Wifi"
    },
    "lana-home" : {
      cidr_block   = "75.84.53.143/32"
      display_name = "Lana's Home Network"
    },
    "liam-home" : {
      cidr_block   = "76.146.71.81/32"
      display_name = "Liam's Home Network"
    }
  }

  # # These are auto-created with the project
  # default_network_id = "projects/${local.project_id}/global/networks/default"
  # default_subnetwork_id = "projects/${local.project_id}/${local.region}/subnetworks/default"
}

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
}

provider "google" {
  project = local.project_id
  region  = local.region
  zone    = local.zone
}

module "gcp_project" {
  source          = "../../modules/project"
  project_id      = local.project_id
  org_id          = local.org_id
  billing_account = local.billing_account
}

module "tfstate" {
  source     = "../../modules/tfstate"
  project_id = local.project_id
}

module "docker_registry" {
  source = "../../modules/docker_registry"
  region = local.region
}

module "nat" {
  source     = "../../modules/nat"
  project_id = local.project_id
  region     = local.region
}

module "dns_zone_base_domain" {
  source = "../../modules/dns_zone"
  domain = local.root_domain
}

module "gke" {
  source              = "../../modules/gke"
  project_id          = local.project_id
  region              = local.region
  authorized_networks = local.authorized_networks
}

# Configure kubernetes provider with Oauth2 access token.
# https://registry.terraform.io/providers/hashicorp/google/latest/docs/data-sources/client_config
# This fetches a new token, which will expire in 1 hour.
data "google_client_config" "default" {}

provider "kubernetes" {
  host                   = "https://${module.gke.cluster.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(module.gke.cluster.master_auth[0].cluster_ca_certificate)

  # config_path = "~/.kube/config"
  # config_context = "eave-staging"

  ignore_annotations = [
    "^autopilot\\.gke\\.io\\/.*",
    "^cloud\\.google\\.com\\/.*"
  ]
}

module "kube_configs" {
  source = "../../kube_configs"
  project_id = local.project_id
  region = local.region
  root_domain = local.root_domain
  docker_repository = module.docker_registry.repository
  METABASE_UI_BIGQUERY_ACCESSOR_GSA_KEY_JSON_B64 = var.METABASE_UI_BIGQUERY_ACCESSOR_GSA_KEY_JSON_B64
  RELEASE = var.RELEASE
  static_ip_names = {
    core_api = module.dns_apps["core-api"].google_compute_global_address.name
    dashboard = module.dns_apps["dashboard"].google_compute_global_address.name
    playground_todoapp = module.dns_apps["playground-todoapp"].google_compute_global_address.name
  }
}

# module "gcp_bigquery" {
#   source     = "../../modules/bigquery"
#   project_id = local.project_id
#   region     = local.region
# }
