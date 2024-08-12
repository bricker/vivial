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

# moved {
#   from = module.playground_todoapp.google_service_account_iam_binding.impersonators
#   to = module.playground_todoapp.google_service_account_iam_binding.app_sa_impersonators
# }

moved {
  from = module.playground_todoapp.google_service_account_iam_binding.impersonators
  to = module.playground_todoapp.google_service_account_iam_binding.app_sa_impersonators[0]
}

moved {
  from = module.core_api_app.module.app_iam_role.google_project_iam_binding.default
  to   = module.core_api_app.google_project_iam_binding.project_app_role_members
}

# moved {
#   from = module.core_api_app.google_service_account_iam_binding.impersonators
#   to = module.core_api_app.google_service_account_iam_binding.app_sa_impersonators
# }

moved {
  from = module.core_api_app.google_service_account_iam_binding.impersonators
  to = module.core_api_app.google_service_account_iam_binding.app_sa_impersonators[0]
}

moved {
  from = module.gcp_secret_manager
  to   = module.secret_manager_secrets
}

moved {
  from = google_compute_firewall.allow_iap_ingress
  to = google_compute_firewall.allow_iap_ingress_to_cloudsql_bastion
}

moved {
  from = module.custom_developer_role.google_project_iam_binding.default
  to = google_project_iam_binding.developer_role_members
}

moved {
  from = module.custom_everybody_role.google_project_iam_binding.default
  to = google_project_iam_binding.everybody_role_members
}

moved {
  from = module.gke_primary.module.custom_gke_node_role.google_project_iam_binding.default
  to = module.gke_primary.google_project_iam_binding.gke_node_role_binding
}

moved {
  from = module.gke_primary.google_project_iam_binding.gke_node_role_binding
  to = module.gke_primary.google_project_iam_binding.gke_node_role_members
}

moved {
  from = module.gke_primary.google_artifact_registry_repository_iam_binding.gke_node_role
  to = module.gke_primary.google_artifact_registry_repository_iam_binding.gke_node_role_docker_repo_members
}