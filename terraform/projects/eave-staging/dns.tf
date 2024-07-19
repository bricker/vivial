module "dns_zone_base_domain" {
  source      = "../../modules/dns_zone"
  root_domain = local.project.root_domain
}

module "dns_zone_pink" {
  source      = "../../modules/dns_zone"
  root_domain = "eave.pink"
}

module "dns_zone_red" {
  source      = "../../modules/dns_zone"
  root_domain = "eave.red"
}

module "dns_zone_blue" {
  source      = "../../modules/dns_zone"
  root_domain = "eave.blue"
}

module "dns_zone_run" {
  source      = "../../modules/dns_zone"
  root_domain = "eave.run"
}

resource "google_dns_record_set" "eave_dot_run" {
  managed_zone = module.dns_zone_run.zone.name
  name         = "*.${module.dns_zone_run.zone.dns_name}"
  type         = "CNAME"
  ttl          = 300
  rrdatas      = ["localhost."]
}