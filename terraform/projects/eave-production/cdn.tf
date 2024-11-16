module "cdn" {
  source                 = "../../modules/cdn"

  resource_domain            = local.resource_domain
  name                   = "cdn"
  google_dns_managed_zone          = module.dns_zone_base_domain.google_dns_managed_zone
  google_certificate_manager_certificate_map   = module.project_base.google_certificate_manager_certificate_map
  google_compute_ssl_policy        = module.project_base.google_compute_ssl_policy
  usage_logs_bucket_name = module.project_base.usage_logs_bucket_name
}
