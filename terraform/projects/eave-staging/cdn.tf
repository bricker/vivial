module "cdn" {
  source                 = "../../modules/cdn"
  resource_domain        = local.resource_domain
  dns_domain             = local.dns_domain
  name                   = "cdn"
  dns_zone_name          = module.dns_zone_base_domain.dns_zone_name
  certificate_map_name   = module.project_base.certificate_map_name
  ssl_policy_name        = module.project_base.ssl_policy_name
  usage_logs_bucket_name = module.project_base.usage_logs_bucket_name
}
