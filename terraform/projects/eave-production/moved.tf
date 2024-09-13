moved {
  from = module.dashboard_app.module.app_iam_role.google_project_iam_binding.default
  to   = module.dashboard_app.google_project_iam_binding.project_app_role_members
}

moved {
  from = module.core_api_app.module.app_iam_role.google_project_iam_binding.default
  to   = module.core_api_app.google_project_iam_binding.project_app_role_members
}

moved {
  from = module.gcp_secret_manager
  to   = module.secret_manager_secrets
}

moved {
  from = module.dns_zone_base_domain.google_dns_record_set.records[0]
  to   = module.dns_zone_base_domain.google_dns_record_set.records["MX_apex"]
}

moved {
  from = module.dns_zone_base_domain.google_dns_record_set.records[1]
  to   = module.dns_zone_base_domain.google_dns_record_set.records["A_apex"]
}

moved {
  from = module.dns_zone_base_domain.google_dns_record_set.records[2]
  to   = module.dns_zone_base_domain.google_dns_record_set.records["TXT_apex"]
}

moved {
  from = module.dns_zone_base_domain.google_dns_record_set.records[3]
  to   = module.dns_zone_base_domain.google_dns_record_set.records["TXT__dmarc"]
}

moved {
  from = module.dns_zone_base_domain.google_dns_record_set.records[4]
  to   = module.dns_zone_base_domain.google_dns_record_set.records["TXT_google._domainkey"]
}

moved {
  from = module.dns_zone_base_domain.google_dns_record_set.records[5]
  to   = module.dns_zone_base_domain.google_dns_record_set.records["CNAME_tlhahrxjw5anplz9yyg7"]
}

moved {
  from = module.dns_zone_base_domain.google_dns_record_set.records[6]
  to   = module.dns_zone_base_domain.google_dns_record_set.records["CNAME_www"]
}

moved {
  from = module.dns_zone_base_domain.google_dns_record_set.records[7]
  to   = module.dns_zone_base_domain.google_dns_record_set.records["CNAME_ala55kg6in7z"]
}

moved {
  from = module.dns_zone_base_domain.google_dns_record_set.records[8]
  to   = module.dns_zone_base_domain.google_dns_record_set.records["CNAME_jjeu6awts77f"]
}

moved {
  from = module.dns_zone_base_domain.google_dns_record_set.records[9]
  to   = module.dns_zone_base_domain.google_dns_record_set.records["CNAME_orgaarcdmnxh"]
}