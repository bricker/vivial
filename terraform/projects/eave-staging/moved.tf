moved {
  from = module.playground_quizapp.module.app_iam_role.google_project_iam_binding.default
  to   = module.playground_quizapp.google_project_iam_binding.project_app_role_members
}

moved {
  from = module.dashboard_app.module.app_iam_role.google_project_iam_binding.default
  to   = module.dashboard_app.google_project_iam_binding.project_app_role_members
}

moved {
  from = module.playground_todoapp.module.app_iam_role.google_project_iam_binding.default
  to   = module.playground_todoapp.google_project_iam_binding.project_app_role_members
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
  from = google_compute_firewall.allow_iap_ingress
  to   = google_compute_firewall.allow_iap_ingress_to_cloudsql_bastion
}

moved {
  from = module.custom_developer_role.google_project_iam_binding.default
  to   = google_project_iam_binding.project_developer_role_members
}

moved {
  from = module.custom_everybody_role.google_project_iam_binding.default
  to   = google_project_iam_binding.project_everybody_role_members
}

moved {
  from = module.gke_primary.module.custom_gke_node_role.google_project_iam_binding.default
  to   = module.gke_primary.google_project_iam_binding.gke_node_role_binding
}

moved {
  from = module.gke_primary.google_project_iam_binding.gke_node_role_binding
  to   = module.gke_primary.google_project_iam_binding.gke_node_role_members
}

moved {
  from = module.gke_primary.google_artifact_registry_repository_iam_binding.gke_node_role
  to   = module.gke_primary.google_artifact_registry_repository_iam_binding.docker_repo_gke_node_role_members
}

moved {
  from = module.core_api_app.google_service_account_iam_binding.impersonators
  to   = module.core_api_app.google_service_account_iam_binding.sa_impersonator_role_members
}

moved {
  from = module.gke_primary.google_project_iam_binding.gke_node_role_members
  to   = module.gke_primary.google_project_iam_binding.project_gke_node_role_members
}


moved {
  from = module.dns_zone_base_domain.google_dns_record_set.records[0]
  to   = module.dns_zone_base_domain.google_dns_record_set.records["TXT_apex"]
}
# moved {
#   from = module.dns_zone_base_domain.google_dns_record_set.records[2]
#   to = module.dns_zone_base_domain.google_dns_record_set.records["TXT_k1._domainkey"]
# }
moved {
  from = module.dns_zone_base_domain.google_dns_record_set.records[1]
  to   = module.dns_zone_base_domain.google_dns_record_set.records["MX_apex"]
}


moved {
  from = module.dns_zone_blue.google_dns_record_set.records[1]
  to   = module.dns_zone_blue.google_dns_record_set.records["TXT_apex"]
}
moved {
  from = module.dns_zone_blue.google_dns_record_set.records[2]
  to   = module.dns_zone_blue.google_dns_record_set.records["TXT_k1._domainkey"]
}
moved {
  from = module.dns_zone_blue.google_dns_record_set.records[0]
  to   = module.dns_zone_blue.google_dns_record_set.records["MX_apex"]
}


moved {
  from = module.dns_zone_pink.google_dns_record_set.records[1]
  to   = module.dns_zone_pink.google_dns_record_set.records["TXT_apex"]
}
moved {
  from = module.dns_zone_pink.google_dns_record_set.records[2]
  to   = module.dns_zone_pink.google_dns_record_set.records["TXT_smtp._domainkey"]
}
moved {
  from = module.dns_zone_pink.google_dns_record_set.records[0]
  to   = module.dns_zone_pink.google_dns_record_set.records["MX_apex"]
}


moved {
  from = module.dns_zone_red.google_dns_record_set.records[1]
  to   = module.dns_zone_red.google_dns_record_set.records["TXT_apex"]
}
moved {
  from = module.dns_zone_red.google_dns_record_set.records[2]
  to   = module.dns_zone_red.google_dns_record_set.records["TXT_mailo._domainkey"]
}
moved {
  from = module.dns_zone_red.google_dns_record_set.records[0]
  to   = module.dns_zone_red.google_dns_record_set.records["MX_apex"]
}


moved {
  from = module.dns_zone_run.google_dns_record_set.records[0]
  to   = module.dns_zone_run.google_dns_record_set.records["A_*"]
}
moved {
  from = module.dns_zone_run.google_dns_record_set.records[2]
  to   = module.dns_zone_run.google_dns_record_set.records["TXT_apex"]
}
moved {
  from = module.dns_zone_run.google_dns_record_set.records[1]
  to   = module.dns_zone_run.google_dns_record_set.records["MX_apex"]
}
moved {
  from = module.dns_zone_run.google_dns_record_set.records[3]
  to   = module.dns_zone_run.google_dns_record_set.records["TXT_smtp._domainkey"]
}
