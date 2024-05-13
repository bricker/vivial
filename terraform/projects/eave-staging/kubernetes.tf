module "gke" {
  source              = "../../modules/gke"
  location = local.project.region # For staging this should be a zone, but I already created it with a region and I didn't want to recreate the whole cluster.
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
    "^cloud\\.google\\.com\\/.*",
  ]
}

module "shared_kubernetes_resources" {
  source = "../../modules/kube_shared_resources"
  project = local.project
}
