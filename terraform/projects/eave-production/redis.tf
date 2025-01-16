module "redis" {
  source = "../../modules/redis"
  google_compute_network = module.project_base.google_compute_network

  redis_user_role_members = [
    module.core_api_app.service_account.member,
  ]
}
