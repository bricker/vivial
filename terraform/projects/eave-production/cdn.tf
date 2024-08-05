module "cdn" {
  source          = "../../modules/cdn"
  root_domain = local.root_domain
  location = local.default_region
  name = "cdn"
  dns_zone_name        = module.dns_zone_base_domain.dns_zone_name
  certificate_map_name = module.project_base.certificate_map_name
  ssl_policy_name = module.project_base.ssl_policy_name
}
