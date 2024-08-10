moved {
  from = module.playground_quizapp.module.app_iam_role.google_project_iam_binding.default
  to = module.playground_quizapp.google_project_iam_binding.gke_gsa_app_role
}

moved {
  from = module.playground_todoapp.module.app_iam_role.google_project_iam_binding.default
  to = module.playground_todoapp.google_project_iam_binding.gke_gsa_app_role
}

moved {
  from = module.dashboard_app.module.app_iam_role.google_project_iam_binding.default
  to = module.dashboard_app.google_project_iam_binding.gke_gsa_app_role
}

moved {
  from = module.core_api_app.module.app_iam_role.google_project_iam_binding.default
  to = module.core_api_app.google_project_iam_binding.gke_gsa_app_role
}

moved {
  from = module.gcp_secret_manager
  to = module.secret_manager_secrets
}
