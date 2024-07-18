locals {
  domain = trimsuffix(google_dns_record_set.cdn.name, ".")
}