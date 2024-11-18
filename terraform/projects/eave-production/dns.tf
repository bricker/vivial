# The DNS Zone configured in this file is _NOT USED_ for vivialapp.com.
# It is missing many important records (eg for Google Workspace).
# It's here because our other domains do use Google's nameservers, so many modules use a DNS zone for naming stuff.

# vivialapp.com DNS is managed in Squarespace and uses Squarespace nameservers.
# If you need to make changes to the vivialapp.com DNS records, go to Squarespace Domains.
# Making changes in this file won't have any effect on the vivialapp.com DNS.

module "dns_zone_base_domain" {
  source     = "../../modules/dns_zone"
  dns_domain = local.dns_domain
  records    = []
}
