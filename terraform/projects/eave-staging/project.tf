module "gcp_project" {
  source          = "../../modules/project"
  project         = local.project
  org_id          = local.org_id
  billing_account = local.billing_account
}

module "tfstate" {
  source  = "../../modules/tfstate"
  project = local.project
}

module "common_gcp_services" {
  source = "../../modules/common_gcp_services"
}

module "common_gce_metadata" {
  source = "../../modules/common_gce_metadata"
}

module "docker_registry" {
  source = "../../modules/docker_registry"
}

module "nat" {
  source     = "../../modules/nat"
  network_id = data.google_compute_network.default.id
}

module "dns_zone_base_domain" {
  source      = "../../modules/dns_zone"
  root_domain = local.project.root_domain
}

module "cloudsql_eave_core" {
  source        = "../../modules/cloudsql_instance"
  project       = local.project
  instance_name = "eave-pg-core"
  network_id    = data.google_compute_network.default.id
}

module "ssl_policy" {
  source = "../../modules/ssl_policy"
}

resource "google_certificate_manager_certificate_map" "default" {
  name = "root-certificate-map"
}

module "cdn" {
  source          = "../../modules/cdn"
  project         = local.project
  dns_zone        = module.dns_zone_base_domain.zone
  certificate_map = google_certificate_manager_certificate_map.default
}

module "gke" {
  source              = "../../modules/gke"
  location            = local.project.region # For staging this should be a zone, but I already created it with a region and I didn't want to recreate the whole cluster.
  authorized_networks = local.authorized_networks
}

module "shared_kubernetes_resources" {
  source                  = "../../modules/kube_shared_resources"
  project                 = local.project
  iap_oauth_client_secret = var.IAP_OAUTH_CLIENT_SECRET
}
